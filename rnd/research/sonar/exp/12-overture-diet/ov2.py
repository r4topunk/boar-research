import duckdb, time, json
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
src = "s3://overturemaps-us-west-2/release/2026-09-23.1/theme=places/type=place/*.parquet"
boxes = {"edmonton": (53.3724, 53.7128, -113.7660, -113.1715), "queens": (40.5567, 40.8599, -74.0700, -73.6001), "bien-hoa": (10.7600, 11.1149, 106.6403, 107.0084)}
out = {}
for city, (y0, y1, x0, x1) in boxes.items():
    t = time.time()
    q = f"""SELECT taxonomy.primary AS cat, count(*) n, count(*) FILTER (WHERE confidence >= 0.7) n_conf
            FROM read_parquet('{src}', hive_partitioning=1)
            WHERE bbox.xmin BETWEEN {x0} AND {x1} AND bbox.ymin BETWEEN {y0} AND {y1}
              AND (taxonomy.primary IN ('vegan_restaurant','vegetarian_restaurant') OR list_contains(taxonomy.alternates,'vegan_restaurant') OR list_contains(taxonomy.alternates,'vegetarian_restaurant') OR basic_category = 'restaurant')
            GROUP BY 1 ORDER BY 2 DESC"""
    rows = con.execute(q).fetchall()
    d = {r[0]: (r[1], r[2]) for r in rows}
    restaurants = sum(v[0] for v in d.values())
    alt = con.execute(f"""SELECT count(*) FROM read_parquet('{src}', hive_partitioning=1)
            WHERE bbox.xmin BETWEEN {x0} AND {x1} AND bbox.ymin BETWEEN {y0} AND {y1}
              AND taxonomy.primary NOT IN ('vegan_restaurant','vegetarian_restaurant')
              AND (list_contains(taxonomy.alternates,'vegan_restaurant') OR list_contains(taxonomy.alternates,'vegetarian_restaurant'))""").fetchone()[0]
    out[city] = {"vegan_primary": d.get("vegan_restaurant"), "vegetarian_primary": d.get("vegetarian_restaurant"), "vegan_or_veg_as_alternate": alt, "all_restaurant_like_rows": restaurants, "seconds": round(time.time() - t)}
    print(city, out[city], flush=True)
json.dump(out, open("overture-diet.json", "w"), indent=1)
