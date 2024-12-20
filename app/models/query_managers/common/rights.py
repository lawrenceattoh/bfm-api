from neomodel import db

from app.models._base import parse_neo_response
from app.models._query_manager import AbstractQueryManager
from app.schemas.common.rights import AttachedRights

_query_update_rights_original = '''
unwind $rights as right
match (asset: Work {id: $node_id})
optional match (asset)-[:SHARE_OWNERSHIP]-(existingRight:Right)
with asset, collect(existingRight) as existingRights, $rights as incomingRights



// process incoming rights
unwind incomingRights as right
optional match (existingRight:Right {id: right.id})
match (deal:Deal {id: right.deal_id})
call apoc.do.when(
    existingRight is null,
    '
    create (nr:Right)
    set nr.perf_share = right.perf_share,
        nr.right_type = right.right_type,
        nr.is_controlled = right.is_controlled,
        nr.territories = right.territories,
        nr.mech_share = right.mech_share,
        nr.licensee = right.licensee,
        nr.updated_at = datetime(),
        nr.updated_by = $rms_user
    with nr, right
    call custom.addNodeId(nr, "RGT") yield node as nrWithId
    return nrWithId as node
    ',
    '
    set existingRight.perf_share = right.perf_share,
        existingRight.right_type = right.right_type,
        existingRight.is_controlled = right.is_controlled,
        existingRight.territories = right.territories,
        existingRight.mech_share = right.mech_share,
        existingRight.licensee = right.licensee,
        existingRight.updated_at = datetime(),
        existingRight.updated_by = $rms_user
    return existingRight as node
    ',
    {right: right, existingRight: existingRight, rms_user: $rms_user}
) yield value
with value.node as r, right, asset, deal, existingRights, incomingRights
merge (asset)-[:SHARE_OWNERSHIP]-(r)
merge (r)-[:BOUGHT_IN]->(deal)
with *

// delete rights not in the incoming request
call {
    with existingRights, incomingRights
    unwind existingRights as existingRight
    with existingRight, [r in incomingRights | r.id] as incomingIds
    foreach (_ in case when not existingRight.id in incomingIds then [1] else [] end |
        detach delete existingRight
    )
    return count(existingRight) as deletedRightsCount
}






// return updated rights
with asset
match (asset)-[:SHARE_OWNERSHIP]-(r)
match (r)-[:BOUGHT_IN]-(d)
return 
    d.id as deal_id, 
    r.id as id, 
    r.perf_share as perf_share, 
    r.right_type as right_type, 
    r.is_controlled as is_controlled, 
    r.territories as territories, 
    r.mech_share as mech_share, 
    r.licensee as licensee


'''

_query_update_rights_new = '''
match (asset:Work {id: $node_id})
with asset, $rights as incomingRights

// First delete rights that are no longer in the incoming set
call (*){
    optional match (asset)-[:SHARE_OWNERSHIP]-(existingRight:Right)
    with incomingRights, collect(existingRight) as existingRights 
    unwind existingRights as existingRight
    with existingRight, [r in incomingRights | r.id] as incomingIds
    call apoc.do.when(
        not existingRight.id in incomingIds,
        'detach delete existingRight',
        '',
        {existingRight: existingRight}
    ) yield value
    return count(value) as deletedRightsCount
} in transactions

// Process incoming rights - only once
with asset, incomingRights
unwind incomingRights as right
optional match (asset)-[:SHARE_OWNERSHIP]-(existingRight:Right {id: right.id})
match (deal:Deal {id: right.deal_id})

// Create or update rights
call apoc.do.when(
    existingRight is null,
    '
    create (nr:Right)
    set nr.perf_share = right.perf_share,
        nr.right_type = right.right_type,
        nr.is_controlled = right.is_controlled,
        nr.territories = right.territories,
        nr.mech_share = right.mech_share,
        nr.third_party_admin = right.third_party_admin, 
        nr.reversion_date = right.reversion_date,
        nr.updated_at = datetime(),
        nr.updated_by = $rms_user
    create (asset)-[:SHARE_OWNERSHIP]->(nr)
    create (nr)-[:BOUGHT_IN]->(deal)
    with nr, right
    call custom.addNodeId(nr, "RGT") yield node as nrWithId
    return nrWithId as node
    ',
    '
    set existingRight.perf_share = right.perf_share,
        existingRight.right_type = right.right_type,
        existingRight.is_controlled = right.is_controlled,
        existingRight.territories = right.territories,
        existingRight.mech_share = right.mech_share,
        existingRight.third_party_admin = right.third_party_admin, 
        existingRight.reversion_date = right.reversion_date,
        existingRight.updated_at = datetime(),
        existingRight.updated_by = $rms_user
    return existingRight as node
    ',
    {right: right, existingRight: existingRight, rms_user: $rms_user, asset: asset, deal: deal}
) yield value

// Return updated rights
with asset
match (asset)-[:SHARE_OWNERSHIP]-(r)
match (r)-[:BOUGHT_IN]-(d)
return 
    d.id as deal_id, 
    r.id as id, 
    r.perf_share as perf_share, 
    r.right_type as right_type, 
    r.is_controlled as is_controlled, 
    r.territories as territories, 
    r.mech_share as mech_share, 
    r.licensee as licensee
'''


class RightsQueryManager(AbstractQueryManager):

    @staticmethod
    def get_attached_rights():
        return '''
            match (asset: Work | Recording {id: $node_id})
            match (asset)-[:SHARE_OWNERSHIP]-(r:Right)
            match (r)-[:BOUGHT_IN]-(d:Deal)
            return 
                    d.id as deal_id, 
                    r.id as id, 
                    r.perf_share as perf_share, 
                    r.right_type as right_type, 
                    r.is_controlled as is_controlled, 
                    r.territories as territories, 
                    r.mechanical_share as mechanical_share, 
                    r.third_party_admin as third_party_admin, 
                    r.reversion_date as reversion_date
                    
        '''

    @staticmethod
    def update_rights():
        return _query_update_rights_new


class RightsNode:

    @staticmethod
    def get_attached_rights(node_id):
        r, s = db.cypher_query(RightsQueryManager.get_attached_rights(), params={'node_id': node_id})
        rights = parse_neo_response(r, s, is_many=True)
        print(rights, 'I AM THE RIGHTS OKAY')
        return AttachedRights(rights=rights)

    @staticmethod
    def update_rights(node_id, rights, rms_user):
        r, s = db.cypher_query(RightsQueryManager.update_rights(),
                               params={'node_id': node_id, 'rights': rights, 'rms_user': rms_user})
        print(rights, 'THIS IS WHAT IS BEING SENT TO NEO4j')
        rights = parse_neo_response(r, s, is_many=True)
        return AttachedRights(rights=rights)
