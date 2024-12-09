from neomodel import db

masters_loadquery = '''
UNWIND $rows AS row

merge (d: Deal {name: row.deal_name})
  on create set d.completed_date = row.completed_date

unwind row.rights_type as rights_type
    merge (rt: RightsType {name: rights_type})


merge (a: Artist {name: row.artist})
merge (t: Track {name: row.title})
merge (rec: Recording {isrc: row.isrc})
merge (c: Copyright {name: row.copyright})
//merge (rt: RightsType {name: row.rights_type})
merge (e: BusinessEntity{name: row.business_entity})


with d, a, t, rec, collect(rt) as rights, c, e
call custom.addNodeId(d, 'DEA') yield node as _d
call custom.addNodeId(t, 'TRK') yield node as _t
call custom.addNodeId(a, 'ART') yield node as _a
call custom.addNodeId(e, 'ENT') yield node as _e

with d, a, t, rec, rt, c, rights
    merge (e)-[:PARENT_CO]-(d) # Look at 
    merge (d)<-[:PURCHASED_ASSET]-(rec)
    merge (rec)-[:RECORDING_OF]->(t)
    merge (t)-[:RECORDED_BY]->(a)
    merge (rt)<-[:OWNERSHIP_TYPE]-(rec)
    unwind rights as rights_type
        merge (c)-[:PARENT_RIGHT]->(rights_type)

with d, a, t, rec 
    unwind [d, t, a, rec] as node
set
    node.is_deleted = false,
    node.created_by = case when node.created_by is null then $rms_user else node.created_by end,
    node.created_at = case when node.created_at is null then datetime() else node.created_at end,
    node.updated_at = datetime(),
    node.updated_by = $rms_user,
    node.status = 'validated',
    node.create_method = 'bulk file import'
return node 
'''

publishing_loadquery = """
UNWIND $rows AS row

merge (p:Publisher {name: 'BELLA FIGURA MUSIC', ipi: '1133481777'})
with case when 
    row.iswc is null 
    then '223336'
    else row.iswc 
    end as iswc, row, p
    
merge (d: Deal {name: row.deal_name})
  on create set d.completed_date = row.completed_date
  

merge (w: Writer {name: row.name, alias: row.alias, ipi:row.ipi})
merge (wrk: Work {name: row.title, _shadow_iswc: iswc, _deal: row.deal_name}) 
on create set 
    wrk.iswc = case when row.iswc <> '' then row.iswc else null end, 
    wrk.is_bfm_owned = row.is_bfm_owned,
    wrk.is_passive = row.is_passive,
    wrk.third_party_admin_expiry = row.third_party_admin_expiry // TODO: Must look into this meaning. Dont like it
    
merge (c: Copyright {name: row.copyright})
merge (e: BusinessEntity{name: row.business_entity})

with d, w, wrk, row, c, e, p
call custom.addNodeId(d, 'DEA') yield node as _d
call custom.addNodeId(w, 'WRI') yield node as _w
call custom.addNodeId(wrk, 'WRK') yield node as _wrk
call custom.addNodeId(p, 'PUB') yield node as _pub 


// IP CHAIN probably doesn't need creating each time. Should search against the node and update.
with w, wrk, d, row, c, e, p
    merge (e)-[:PARENT_CO]-(d) // Look at 
    merge (d)-[:PURCHASED_ASSET]->(wrk)
    merge (d)-[:DEAL_TYPE]->(c)
    merge (wrk)<-[:ROYALTY_SHARE]-(ip: IpChain)
    merge (w)-[ws: WRITER_SHARE]->(ip)
    set ws.perf_share= round(tofloat(row.ownershippcnt), 2)
    merge (p)-[ps: PUBLISHER_SHARE]->(ip)
    set ps.mechanical_share = round(tofloat(row.ownershippcnt) * 2, 2)
    
    with w, wrk, d, row, c, e, ps, ws
    call {
        with row, ps, ws
        foreach (rt IN row.rights_type |
            foreach (_ IN CASE WHEN rt = 'publisher share' then [1] else [] end |
                set ps.is_bfm_royalty = true
            )
            foreach (_ IN CASE WHEN rt = 'writer share' then [1] else [] end |
                set ws.is_bfm_royalty = true
            )
        )
    }
            
with distinct w, wrk, d 
    unwind [w, wrk, d] as node
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

prs_load_query = '''


'''

publishing_loadquery_new = """
UNWIND $rows AS row

match (bg: BusinessGroup {id: row.business_group_id}) 
with row, bg
merge (p:Publisher {name: 'BELLA FIGURA MUSIC', ipi: '1133481777'})

with case when 
    row.iswc is null 
    then '223336'
    else row.iswc 
    end as iswc, row, p, bg

merge (d: Deal {name: row.deal_name})
  on create set d.completed_date = row.completed_date


merge (w: Writer {name: row.name, alias: row.alias, ipi:row.ipi})
merge (wrk: Work {name: row.title, _shadow_iswc: iswc, _deal: row.deal_name}) 
on create set 
    wrk.iswc = case when row.iswc <> '' then row.iswc else null end, 
    wrk.reversion_date = case when row.reversion_date <> '' then row.reversion_date else null end,  
    wrk.territories = case when row.territories <> '' then row.territories else null end 

merge (c: Copyright {name: row.main_copyright})

with d, w, wrk, row, c, bg, p
call custom.addNodeId(d, 'DEA') yield node as _d
call custom.addNodeId(w, 'WRI') yield node as _w
call custom.addNodeId(wrk, 'WRK') yield node as _wrk
call custom.addNodeId(p, 'PUB') yield node as _pub 



// IP CHAIN probably doesn't need creating each time. Should search against the node and update.
with w, wrk, d, row, c, bg, p
    merge (bg)-[:PARENT_CO]-(d) // Look at 
    merge (d)-[:PURCHASED_ASSET]->(wrk)
    merge (d)-[:DEAL_TYPE]->(c)
    merge (wrk)<-[:ROYALTY_SHARE]-(ip: IpChain)
    merge (w)-[ws:WRITER_SHARE]->(ip)

    
WITH w, wrk, d, row, c, bg, p, ip,ws
CALL (*) {
    foreach (_ in case when row.right_type = 'publisher_share' then [1] else [] end |
        merge (p)-[ps:PUBLISHER_SHARE]->(ip)
        set ps.perf_share = tofloat(row.ownership_pcnt), 
        ps.is_controlled = row.is_controlled, 
        ps.deal_id = d.id 
        
        foreach(_ in case when row.is_controlled then [1] else [] end |
            set ip.mechanical_share = tofloat(row.ownership_pcnt) * 2
            
    ))
    foreach (_ in case when row.right_type = 'writer_share' then [1] else [] end |
        //merge (w)-[ws:WRITER_SHARE]->(ip)
        set 
            ws.perf_share = tofloat(row.ownership_pcnt), 
            ws.deal_id = d.id 
            
    )
    return null as  _
}

with distinct w, wrk, d , p
    unwind [w, wrk, d,p] as node
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

publishing_loadquery_new = """

UNWIND $rows AS row
with case when 
    row.iswc is null 
    then '223336'
    else row.iswc 
    end as iswc, row

match (d: Deal {id: row.deal_id}) // Must be created before the schedule is loaded


merge (c: MainCopyrightType {name: 'publishing'})
merge (w: Writer {name: row.name, alias: row.alias, ipi:row.ipi})
merge (wrk: Work {name: row.title, _shadow_iswc: iswc, _deal: row.deal_id}) 
on create set 
    wrk.iswc = case when row.iswc <> '' then row.iswc else null end, 
    wrk.reversion_date = case when row.reversion_date <> '' then row.reversion_date else null end,  
    wrk.territories = case when row.territories <> '' then row.territories else null end 

with d, w, wrk, row,c
call custom.addNodeId(w, 'WRI') yield node as _w
call custom.addNodeId(wrk, 'WRK') yield node as _wrk


with w, wrk, d, row, c
    merge (d)-[:PURCHASED_ASSET]->(wrk)
    merge (d)-[:DEAL_TYPE]->(c)
    merge (wrk)<-[:ROYALTY_SHARE]-(ip: IpChain)
    merge (w)-[ws:WRITER_SHARE]->(ip)

with *
match (p:Publisher {ipi: '1133481777'})
WITH w, wrk, d, row, ip, p, ws
CALL (*) {
    foreach (_ in case when row.right_type = 'publisher_share' then [1] else [] end |
        merge (p)-[ps:PUBLISHER_SHARE]->(ip)
        set ps.perf_share = tofloat(row.ownership_pcnt), 
        ps.is_controlled = row.is_controlled, 
        ps.deal_id = d.id 

        foreach(_ in case when row.is_controlled then [1] else [] end |
            set ip.mechanical_share = tofloat(row.ownership_pcnt) * 2

    ))
    foreach (_ in case when row.right_type = 'writer_share' then [1] else [] end |
        //merge (w)-[ws:WRITER_SHARE]->(ip)
        set 
            ws.perf_share = tofloat(row.ownership_pcnt), 
            ws.deal_id = d.id 

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
    print(masters_loadquery)
    data, schema = db.cypher_query(masters_loadquery, params={'rows': list(rows), 'rms_user': rms_user})
    return data


def publishing_load_schedule_into_db(rows, rms_user):
    data, schema = db.cypher_query(publishing_loadquery_new, params={'rows': list(rows), 'rms_user': rms_user})
    return data


def add_prs(rows, rms_user):
    data, schema = db.cypher_query(publishing_loadquery, params={'rows': list(rows), 'rms_user': rms_user})
    return data
