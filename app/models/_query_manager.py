from abc import ABC, abstractmethod

from jinja2 import Template


class AQMBase(ABC):
    _base_params = [
        "status", "created_by", "created_at",
        "updated_at", "updated_by", "create_method", "is_deleted"
    ]

    def add_base_params(self, alias: str) -> str:
        template = '''
        {% for param in params %}
        {{ alias }}.{{ param }} as {{ param }}{%- if not loop.last -%}, {% endif %}
        {% endfor %}
        '''
        return Template(template).render(alias=alias, params=self._base_params)

    @staticmethod
    def with_pagination(offset: int, limit: int, order: str, order_key: str) -> str:
        return f"skip {offset} limit {limit} order by {order_key} {order}"


class AbstractQueryManager(AQMBase, ABC):

    def __init__(self, alias: str, label: str, _id: str):
        self.alias = alias
        self.label = label
        self._id = _id

    @property
    def _read_one(self) -> str:
        return f"match ({self.alias}: {self.label} {{id:$id, is_deleted:False}})"

    @property
    def _read_all(self) -> str:
        return f"match ({self.alias}: {self.label} {{is_deleted: False}})"

    @property
    def _read_all_count(self) -> str:
        return f"return count(distinct {self.alias}.id)"

    @property
    def _create_id(self) -> str:
        return f"""
        with {self.alias}
        call custom.addNodeId({self.alias}, '{self._id}') yield node as ___disposed_var
        with {self.alias}
        """

    @property
    def _set_defaults(self) -> str:
        return f"""
        set 
            {self.alias}.is_deleted = false,
            {self.alias}.created_by = case when {self.alias}.created_by is null then $rms_user else {self.alias}.created_by end,
            {self.alias}.created_at = case when {self.alias}.created_at is null then datetime() else {self.alias}.created_at end,
            {self.alias}.updated_by = $rms_user,
            {self.alias}.updated_at = datetime(),
            {self.alias}.create_method = 'user generated',
            {self.alias}.status = case when {self.alias}.status is null then 'unvalidated' else {self.alias}.status end
        """

    @property
    def _update(self) -> str:
        return f"""
            with *, $params.node_params as nodeParams
            call (*) {{ 
            with nodeParams, {self.alias}
            where nodeParams is not null
            set {self.alias} += $params.node_params, 
                {self.alias}.updated_at = datetime(),
                {self.alias}.updated_by = $rms_user
            }}
        """

    def delete(self) -> str:
        return f"""
        {self._read_one}
        set {self.alias}.is_deleted = True,
            {self.alias}.deleted_at = datetime(),
            {self.alias}.name = 'DELETED_NODE_' + {self.alias}.name
        return {self.alias}
        """

    def create(self) -> str:
        return "\n".join([
            self._create,
            self._create_id,
            self._set_defaults,
            self._with_relations,
            self._return()
        ])

    def read_one(self) -> str:
        return "\n".join([self._read_one, self._search, self._return()])

    def read_all(self) -> str:
        return "\n".join([self._read_all, self._search, self._return()])

    def read_all_count(self) -> str:
        return "\n".join([self._read_all, self._search, self._read_all_count])

    def update(self) -> str:
        return "\n".join([self._read_one,
                          self._update,
                          self._with_relations,
                          self._return()])

    @property
    @abstractmethod
    def _create(self) -> str:
        pass

    @property
    @abstractmethod
    def _search(self) -> str:
        pass

    @property
    @abstractmethod
    def _return(self) -> str:
        pass

    @property
    def _with_relations(self) -> str:
        return ''
