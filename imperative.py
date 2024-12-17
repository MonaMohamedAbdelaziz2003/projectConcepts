import pyodbc
import datetime

# إعداد الاتصال بقاعدة البيانات
server = 'BESHOY'
database = 'StockManagementSystem'
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# قائمة الخيارات
def menu():
    while True:
        print("\n--- Stock Management System ---")
        print("1. Add Product")
        print("2. Update Quantity")
        print("3. Remove Product")
        print("4. Process Order")
        print("5. Cancel Order")
        print("6. Notify Low Stock")
        print("7. Generate Reports")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_product()
        elif choice == '2':
            update_quantity()
        elif choice == '3':
            remove_product()
        elif choice == '4':
            process_order()
        elif choice == '5':
            cancel_order()
        elif choice == '6':
            notify_low_stock()
        elif choice == '7':
            generate_reports()
        elif choice == '8':
            conn.close()
            break
        else:
            print("Invalid choice. Please try again.")

# إضافة منتج جديد
def add_product():
    product_name = input("Enter product name: ")
    price = float(input("Enter product price: "))
    quantity = int(input("Enter product quantity: "))
    query = "INSERT INTO Product (ProductName, Price, Quantity) VALUES ('{}', {}, {})".format(
        product_name, price, quantity)
    cursor.execute(query)
    conn.commit()
    print("Product '{}' added successfully.".format(product_name))

# تحديث الكمية
def update_quantity():
    product_id = int(input("Enter product ID to update: "))
    new_quantity = int(input("Enter new quantity: "))
    query = "UPDATE Product SET Quantity = {} WHERE ProductID = {}".format(new_quantity, product_id)
    cursor.execute(query)
    conn.commit()
    print("Product ID {} updated successfully.".format(product_id))

# حذف منتج
def remove_product():
    product_id = int(input("Enter product ID to remove: "))
    query = "DELETE FROM Product WHERE ProductID = {}".format(product_id)
    cursor.execute(query)
    conn.commit()
    print("Product ID {} removed successfully.".format(product_id))

# معالجة طلب جديد
def process_order():
    order_date = datetime.datetime.now().date()
    total_price = 0
    order_items = []

    while True:
        product_id = int(input("Enter product ID: "))
        quantity = int(input("Enter quantity: "))
        query = "SELECT Price, Quantity FROM Product WHERE ProductID = {}".format(product_id)
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            price = result[0]
            available_quantity = result[1]
            if available_quantity >= quantity:
                order_items.append((product_id, quantity, price * quantity))
                total_price += price * quantity
            else:
                print("Insufficient stock for Product ID {}. Available: {}.".format(product_id, available_quantity))
        else:
            print("Product ID {} not found.".format(product_id))

        more = input("Add more items? (yes/no): ").lower()
        if more != 'yes':
            break

    query = "INSERT INTO [Order] (OrderDate, TotalPrice) VALUES ('{}', {})".format(order_date, total_price)
    cursor.execute(query)
    conn.commit()

    order_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

    for item in order_items:
        product_id = item[0]
        quantity = item[1]
        query = "INSERT INTO OrderDetails (OrderID, ProductID, Quantity) VALUES ({}, {}, {})".format(order_id, product_id, quantity)
        cursor.execute(query)
        query = "UPDATE Product SET Quantity = Quantity - {} WHERE ProductID = {}".format(quantity, product_id)
        cursor.execute(query)
    conn.commit()

    print("Order processed successfully. Order ID: {}, Total Price: {}.".format(order_id, total_price))

# إلغاء الطلب
def cancel_order():
    order_id = int(input("Enter order ID to cancel: "))
    query = "SELECT ProductID, Quantity FROM OrderDetails WHERE OrderID = {}".format(order_id)
    cursor.execute(query)
    order_details = cursor.fetchall()

    for detail in order_details:
        product_id = detail[0]
        quantity = detail[1]
        query = "UPDATE Product SET Quantity = Quantity + {} WHERE ProductID = {}".format(quantity, product_id)
        cursor.execute(query)

    cursor.execute("DELETE FROM OrderDetails WHERE OrderID = {}".format(order_id))
    cursor.execute("DELETE FROM [Order] WHERE OrderID = {}".format(order_id))
    conn.commit()

    print("Order ID {} cancelled successfully.".format(order_id))

# إخطار المنتجات منخفضة المخزون
def notify_low_stock():
    threshold = int(input("Enter stock threshold: "))
    query = "SELECT ProductID, ProductName, Quantity FROM Product WHERE Quantity < {}".format(threshold)
    cursor.execute(query)
    low_stock_products = cursor.fetchall()

    for product in low_stock_products:
        print("Product ID: {}, Name: {}, Quantity: {}".format(product[0], product[1], product[2]))
    if not low_stock_products:
        print("No products are below the threshold.")

# تقارير المخزون
def generate_reports():
    query = "SELECT ProductName, Quantity FROM Product WHERE Quantity < 5"
    cursor.execute(query)
    low_stock_items = cursor.fetchall()

    query = "SELECT SUM(TotalPrice) FROM [Order]"
    cursor.execute(query)
    total_sales = cursor.fetchone()[0] or 0

    query = "SELECT SUM(Price * Quantity) FROM Product"
    cursor.execute(query)
    inventory_value = cursor.fetchone()[0] or 0

    print("Low Stock Items:")
    for item in low_stock_items:
        print("Product: {}, Quantity: {}".format(item[0], item[1]))
    print("Total Sales: {}".format(total_sales))
    print("Inventory Value: {}".format(inventory_value))

# تشغيل البرنامج
menu()