import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum

spark = SparkSession.builder.appName('productStatSpark').getOrCreate()

DATABASE_URL = os.environ['DATABASE_URL']

product = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.product').option('user', 'root').option('password', 'root').load()
productOrder = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.product_order').option('user', 'root').option('password', 'root').load()
order = spark.read.format('jdbc').option('driver', 'com.mysql.cj.jdbc.Driver').option('url', f'jdbc:mysql://{DATABASE_URL}:3306/store').option('dbtable', 'store.order').option('user', 'root').option('password', 'root').load()

sold = product.join(productOrder, product['id'] == productOrder['productId']).join(order, order['id'] == productOrder['orderId']).where(order['status'] == 'COMPLETE').groupBy(product['name']).agg(sum(productOrder['quantity']).alias('sold')).filter(col('sold') > 0).select(product['name'], col('sold'))
waiting = product.join(productOrder, product['id'] == productOrder['productId']).join(order, order['id'] == productOrder['orderId']).where(order['status'] != 'COMPLETE').groupBy(product['name']).agg(sum(productOrder['quantity']).alias('waiting')).filter(col('waiting') > 0).select(product['name'], col('waiting'))

joined = sold.join(waiting, on = 'name', how = 'outer').na.fill(0)

jsonArray = joined.toJSON().collect()
jsonArray = '{"statistics": [' + ','.join(jsonArray) + ']}'

with open(sys.argv[1], 'w') as file:
    file.write(jsonArray)

spark.stop()
