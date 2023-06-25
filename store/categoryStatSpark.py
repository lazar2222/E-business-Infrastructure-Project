import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, desc

spark = SparkSession.builder.appName('categoryStatSpark').getOrCreate()

DATABASE_URL = os.environ['DATABASE_URL']

category = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.category').option('user', 'root').option('password', 'root').load()
productCategory = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.product_category').option('user', 'root').option('password', 'root').load()
product = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.product').option('user', 'root').option('password', 'root').load()
productOrder = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.product_order').option('user', 'root').option('password', 'root').load()
order = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.order').option('user', 'root').option('password', 'root').load()

categories = category.alias('a').join(productCategory, category['id'] == productCategory['categoryId']).join(product, product['id'] == productCategory['productId']).join(productOrder, product['id'] == productOrder['productId']).join(order, order['id'] == productOrder['orderId']).where(order['status'] == 'COMPLETE').groupBy(category['name']).agg(sum(productOrder['quantity']).alias('val')).alias('a').join(category.alias('b'), col("a.name") == col("b.name"), how = 'outer').orderBy(desc('val'), 'b.name').select('b.name')

jsonArray = categories.toJSON().collect()
jsonArray = [s[8:-1] for s in jsonArray]
jsonArray = '{"statistics": [' + ','.join(jsonArray) + ']}'

with open(sys.argv[1], 'w') as file:
    file.write(jsonArray)

spark.stop()
