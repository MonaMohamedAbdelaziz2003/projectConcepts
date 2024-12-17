CREATE DATABASE StockManagementSystem;

USE StockManagementSystem;


CREATE TABLE Product (
    ProductID INT PRIMARY KEY IDENTITY,
    ProductName NVARCHAR(50) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,  
    Quantity INT NOT NULL CHECK (Quantity >= 0)
);


CREATE TABLE [Order] (
    OrderID INT PRIMARY KEY IDENTITY,
    OrderDate DATETIME,
    TotalPrice DECIMAL(10, 2) NOT NULL  
);


CREATE TABLE OrderDetails (
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    PRIMARY KEY (OrderID, ProductID),
    FOREIGN KEY (OrderID) REFERENCES [Order](OrderID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);


INSERT INTO Product (ProductName, Price, Quantity) VALUES
('Apple', 5.00, 100),
('Banana', 3.00, 150),
('Orange', 4.00, 120),
('Grapes', 8.00, 80),
('Watermelon', 15.00, 60),
('Mango', 12.00, 90),
('Strawberry', 10.00, 70),
('Kiwi', 7.00, 110),
('Pineapple', 20.00, 50),
('Peach', 6.00, 130);


INSERT INTO [Order] (TotalPrice) VALUES
(1000.00),
(450.00),
(300.00),
(1200.00),
(800.00),
(1500.00),
(600.00),
(700.00),
(550.00),
(900.00);


INSERT INTO OrderDetails (OrderID, ProductID, Quantity) VALUES
(1, 1, 10),  
(1, 2, 5),   
(1, 3, 8),   
(2, 4, 7),   
(2, 5, 3),  
(3, 6, 4),   
(4, 7, 6),   
(4, 8, 2),   
(5, 9, 1),   
(5, 10, 10); 