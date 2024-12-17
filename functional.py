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

# 1. دالة لإضافة منتج جديد
def add_product(product_name, price, quantity):
    query = f"INSERT INTO Product (ProductName, Price, Quantity) VALUES ('{product_name}', {price}, {quantity})"
    cursor.execute(query)
    conn.commit()
    return f"Product '{product_name}' added successfully."

def update_product_quantity(product_id, new_quantity):
    # التحقق مما إذا كان المنتج موجودًا أم لا
    query = f"SELECT Quantity FROM Product WHERE ProductID = {product_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    
    if not result:
        return f"Product with ID {product_id} does not exist."
    
    # التحديث مباشرة بالكمية الجديدة
    update_query = f"UPDATE Product SET Quantity = {new_quantity} WHERE ProductID = {product_id}"
    cursor.execute(update_query)
    conn.commit()
    
    return f"Product ID {product_id} quantity updated to {new_quantity}."

# دالة لحذف منتج من قاعدة البيانات
def remove_product(product_id):
    # التحقق من وجود المنتج
    query = f"SELECT ProductName FROM Product WHERE ProductID = {product_id}"
    cursor.execute(query)
    result = cursor.fetchone()

    if not result:
        return f"Product with ID {product_id} does not exist."

    # حذف السجلات المرتبطة في OrderDetails
    delete_details_query = f"DELETE FROM OrderDetails WHERE ProductID = {product_id}"
    cursor.execute(delete_details_query)
    conn.commit()

    # حذف المنتج من جدول Product
    delete_product_query = f"DELETE FROM Product WHERE ProductID = {product_id}"
    cursor.execute(delete_product_query)
    conn.commit()

    return f"Product '{result[0]}' with ID {product_id} and related records have been removed successfully."


# 3. دالة لمعالجة الطلبات
def process_order(order_details):
    order_date = datetime.datetime.now().date()
    total_price = 0

    # تحقق من توفر الكمية وحساب السعر الإجمالي
    for product_id, quantity in order_details:
        query = f"SELECT Price, Quantity FROM Product WHERE ProductID = {product_id}"
        cursor.execute(query)
        result = cursor.fetchone()
        if not result:
            return f"Product with ID {product_id} does not exist."
        
        price, current_quantity = result
        if current_quantity < quantity:
            return f"Insufficient stock for product ID {product_id}. Available: {current_quantity}."
        
        total_price += price * quantity

    # تحديث الكميات
    for product_id, quantity in order_details:
        update_product_quantity(product_id, -quantity)

    # إدخال الطلب في جدول Order
    insert_order_query = f"INSERT INTO [Order] (OrderDate, TotalPrice) VALUES ('{order_date}', {total_price})"
    cursor.execute(insert_order_query)
    conn.commit()

    # الحصول على OrderID
    order_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

    # إدخال تفاصيل الطلب في جدول OrderDetails
    for product_id, quantity in order_details:
        insert_details_query = f"INSERT INTO OrderDetails (OrderID, ProductID, Quantity) VALUES ({order_id}, {product_id}, {quantity})"
        cursor.execute(insert_details_query)
    conn.commit()
    return f"Order processed successfully with total price {total_price}."

# 4. دالة لإلغاء طلب
def cancel_order(order_id):
    # استرجاع تفاصيل الطلب
    query = f"SELECT ProductID, Quantity FROM OrderDetails WHERE OrderID = {order_id}"
    cursor.execute(query)
    order_details = cursor.fetchall()

    if not order_details:
        return f"Order with ID {order_id} does not exist."

    # استعادة الكميات
    for product_id, quantity in order_details:
        update_product_quantity(product_id, quantity)

    # حذف تفاصيل الطلب والطلب نفسه
    delete_details_query = f"DELETE FROM OrderDetails WHERE OrderID = {order_id}"
    delete_order_query = f"DELETE FROM [Order] WHERE OrderID = {order_id}"
    cursor.execute(delete_details_query)
    cursor.execute(delete_order_query)
    conn.commit()
    return f"Order ID {order_id} cancelled successfully."

# 5. دالة لإشعار المخزون المنخفض
def notify_low_stock(threshold):
    query = f"SELECT ProductID, ProductName, Quantity FROM Product WHERE Quantity < {threshold}"
    cursor.execute(query)
    low_stock_items = cursor.fetchall()
    return [(item[0], item[1], item[2]) for item in low_stock_items]

# 6. دالة لتوليد التقارير
def generate_reports():
    # المنتجات منخفضة المخزون
    low_stock_query = "SELECT ProductID, ProductName, Quantity FROM Product WHERE Quantity < 5"
    cursor.execute(low_stock_query)
    low_stock_items = cursor.fetchall()

    # القيمة الإجمالية للمخزون
    inventory_value_query = "SELECT SUM(Price * Quantity) FROM Product"
    cursor.execute(inventory_value_query)
    inventory_value = cursor.fetchone()[0]

    return {
        "low_stock_items": [(item[0], item[1], item[2]) for item in low_stock_items],
        "inventory_value": inventory_value
    }

# 7. القائمة الرئيسية
def main():
    while True:
        print("\n--- Stock Management System ---")
        print("1. Add Product")
        print("2. Update Product Quantity")
        print("3. Remove Product")
        print("4. Process Order")
        print("5. Cancel Order")
        print("6. Notify Low Stock")
        print("7. Generate Reports")
        print("8. Exit")
        
        choice = input("Enter your choice: ")
        if choice == '1':
            name = input("Enter product name: ")
            price = float(input("Enter price: "))
            quantity = int(input("Enter quantity: "))
            print(add_product(name, price, quantity))
        elif choice == '2':
            product_id = int(input("Enter product ID: "))
            quantity_change = int(input("Enter quantity change: "))
            print(update_product_quantity(product_id, quantity_change))
        elif choice == '3':
             product_id = int(input("Enter product ID to remove: "))
             print(remove_product(product_id))
        elif choice == '4':
            order_details = []
            while True:
                product_id = int(input("Enter product ID: "))
                quantity = int(input("Enter quantity: "))
                order_details.append((product_id, quantity))
                more = input("Add more items? (yes/no): ").lower()
                if more != 'yes':
                    break
            print(process_order(order_details))
        elif choice == '5':
            order_id = int(input("Enter order ID: "))
            print(cancel_order(order_id))
        elif choice == '6':
            threshold = int(input("Enter low stock threshold: "))
            print(notify_low_stock(threshold))
        elif choice == '7':
            reports = generate_reports()
            print("Low Stock Items:", reports["low_stock_items"])
            print("Inventory Value:", reports["inventory_value"])
        elif choice == '8':
            conn.close()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()