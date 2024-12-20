from neomodel import db

masters_loadquery = '''

UNWIND $rows AS row
WITH row
WHERE row.artist IS NOT NULL

MATCH (d: Deal {id: row.deal_id})

WITH CASE 
       WHEN row.isrc IS NULL OR row.isrc = "" 
       THEN '19900706'
       ELSE row.isrc 
     END AS isrc, row, d

MERGE (a: Artist {name: trim(row.artist)})
MERGE (t: Track {name: toupper(trim(row.title)), _artist: tolower(trim(row.artist))})
MERGE (rec: Recording {isrc: toupper(trim(isrc)), _title: tolower(trim(row.title)), _artist: tolower(trim(row.artist))})

WITH a, t, rec, d, row

CALL custom.addNodeId(t, 'TRK') YIELD node AS _t
CALL custom.addNodeId(a, 'ART') YIELD node AS _a
CALL custom.addNodeId(rec, 'REC') YIELD node AS _r

WITH a, t, rec, d, row

MERGE (d)<-[:PURCHASED_ASSET]-(rec)
MERGE (rec)-[:VERSION_OF]->(t)
MERGE (t)-[:RECORDED_BY]->(a)

WITH a, t, rec, row, d

CALL (*) {
    merge (rec)-[ps:SHARE_OWNERSHIP]-(r: Right {right_type: row.right_type})  // Needs reviewing. 
    with r
    CALL custom.addNodeId(r, 'RGT') YIELD node AS _rgt
    SET r.is_controlled = row.is_controlled, 
        r.territories = row.territories, 
        r.reversion_date = row.reversion_date, 
        r.third_party_admin = row.third_party_admin
    MERGE (d)<-[:BOUGHT_IN]-(r)
    RETURN null AS _
}

WITH a, t, rec
UNWIND [t, a, rec] AS node
SET node.is_deleted = false,
    node.created_by = CASE WHEN node.created_by IS NULL THEN $rms_user ELSE node.created_by END,
    node.created_at = CASE WHEN node.created_at IS NULL THEN datetime() ELSE node.created_at END,
    node.updated_at = datetime(),
    node.updated_by = $rms_user,
    node.status = 'validated',
    node.create_method = 'bulk file import'

WITH t
RETURN collect(DISTINCT t.id) AS created_tracks

'''

publishing_loadquery_new = """

UNWIND $rows AS row
with row 
where row.name is not null 

with case when 
    row.iswc is null 
    then '223336'
    else row.iswc 
    end as iswc, row

match (d: Deal {id: row.deal_id}) // Must be created before the schedule is loaded. Would have better checks in place but I have been given terrible requirements and this is the third version of the same api. 


merge (c: MainCopyrightType {name: 'publishing'})
merge (w: Writer {name: row.name, alias: row.alias, ipi:row.ipi})
merge (wrk: Work {name: row.title, _shadow_iswc: iswc, _deal: row.deal_id}) 
on create set 
    wrk.iswc = case when row.iswc <> '' then row.iswc else null end 

with d, w, wrk, row,c
call custom.addNodeId(w, 'WRI') yield node as _w
call custom.addNodeId(wrk, 'WRK') yield node as _wrk

with w, wrk, d, row, c
    merge (d)-[:PURCHASED_ASSET]->(wrk)
    merge (d)-[:DEAL_TYPE]->(c)
    merge (wrk)<-[:WRITTEN_BY]-(w)
    
with *
CALL (*) {
    merge (wrk)-[ps:SHARE_OWNERSHIP]-(r: Right {right_type: row.right_type}) 
    with *
    call custom.addNodeId(r, 'RGT') yield node as _r
    set r.perf_share = tofloat(row.ownership_pcnt), 
        r.is_controlled = row.is_controlled, 
        r.territories = row.territories, 
        r.reversion_date = row.reversion_date, 
        r.third_party_admin = row.third_party_admin
    merge (d)<-[:BOUGHT_IN]-(r)

    foreach(_ in case when row.is_controlled and row.calculate_mech_share and row.right_type = 'publisher_share'then [1] else [] end |
        set r.mechanical_share = tofloat(row.ownership_pcnt) * 2

    )
    return null as  _
}


with distinct w, wrk
    unwind [w, wrk] as node
set
    node.is_deleted = false,
    node.created_by = case when node.created_by is null then $rms_user else node.created_by end,
    node.created_at = case when node.created_at is null then datetime() else node.created_at end,
    node.updated_at = datetime(),
    node.updated_by = $rms_user,
    node.status = 'validated', 
    node.create_method = 'bulk file import'

with wrk, w

return w
"""


def masters_load_schedule_into_db(rows, rms_user):
    data, schema = db.cypher_query(masters_loadquery, params={'rows': list(rows), 'rms_user': rms_user})
    return data


def publishing_load_schedule_into_db(rows, rms_user):
    data, schema = db.cypher_query(publishing_loadquery_new, params={'rows': list(rows), 'rms_user': rms_user})
    return data


# def add_prs(rows, rms_user):
#     data, schema = db.cypher_query(publishing_loadquery, params={'rows': list(rows), 'rms_user': rms_user})
#     return data
