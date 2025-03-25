GET_FILE_CHANGE_ID_WITH_TWO_METHOD_CHANGES = '''
select id from
(select file_change.file_change_id as id, count(*) as change_count
    from file_change join method_change on file_change.file_change_id=method_change.file_change_id
    where programming_language=?
    group by file_change.file_change_id)
where change_count=2'''

GET_FILE_CHANGE_ID_FROM_CVE_ID = '''
select file_change.file_change_id as id
from file_change join commits on file_change.hash=commits.hash
    join fixes on commits.hash=fixes.hash
where cve_id=?
'''

# TODO: diff?
GET_METHOD_INFO_FROM_FILE_CHANGES_FOR_GIVEN_CVE = '''
select method_change.name, before_change, method_change.file_change_id, code, new_path, signature
from method_change join file_change
on method_change.file_change_id=file_change.file_change_id
where method_change.file_change_id in
    (select file_change.file_change_id as id
    from file_change
    join method_change on file_change.file_change_id=method_change.file_change_id
    join commits on file_change.hash=commits.hash join fixes on commits.hash=fixes.hash
    where cve_id=?
    group by file_change.file_change_id having count(*)=2)
order by method_change.file_change_id
'''