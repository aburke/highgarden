select pu.id as user_id
    ,concat(pu.first_name, ' ', pu.last_name) as user_name
    ,c.id as company_id
    ,c.name as company_name
from {{ var('platform_user_company') }} puc
    inner join {{ var('company') }} c on puc.company_id = c.id
    inner join {{ var('platform_user') }} pu on puc.platform_user_id = pu.id