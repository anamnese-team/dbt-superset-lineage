from dbt_superset_lineage.push_descriptions import extract_certification_from_table


def test_extract_certification_with_nested_meta_and_freshness():
    table = {
        "meta": {
            "certification": {
                "certified_by": "Data Platform",
                "details": "Source of truth for revenue metrics"
            },
            "freshness": "15m"
        }
    }

    certification = extract_certification_from_table(table)

    assert certification["certified_by"] == "Data Platform"
    assert certification["details"] == "Freshness: 15m | Source of truth for revenue metrics"
