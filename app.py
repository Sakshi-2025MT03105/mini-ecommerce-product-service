
from flask import Flask, jsonify, request
from database import create_table, get_db_connection

# Create the Flask application
app = Flask(__name__)

# Create the products database table
create_table()


# Health check API
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "success",
        "message": "Product Service is running"
    })



# Add Product API
@app.route('/products', methods=['POST'])
def add_product():

    data = request.get_json()

    # Check whether all required details are provided
    if not data or not all(key in data for key in ['name', 'price', 'stock']):
        return jsonify({
            "error": "Please provide name, price and stock"
        }), 400

    try:
        name = data['name']
        price = float(data['price'])
        stock = int(data['stock'])

        if not name.strip() or price < 0 or stock < 0:
            return jsonify({
                "error": "Name must not be empty and price and stock must be non-negative"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid price or stock value"
        }), 400

    connection = get_db_connection()

    connection.execute(
        'INSERT INTO products (name, price, stock) VALUES (?, ?, ?)',
        (name.strip(), price, stock)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Product added successfully"
    }), 201


# Get All Products API

@app.route('/products', methods=['GET'])
def get_all_products():
    connection = get_db_connection()

    products = connection.execute(
        'SELECT * FROM products'
    ).fetchall()

    connection.close()

    product_list = []

    for product in products:
        product_list.append({
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "stock": product["stock"]
        })

    return jsonify(product_list), 200


# Get Product by ID API
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):

    connection = get_db_connection()

    product = connection.execute(
        'SELECT * FROM products WHERE id = ?',
        (product_id,)
    ).fetchone()

    connection.close()

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify({
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "stock": product["stock"]
    }), 200

   
# Update Product API
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):

    data = request.get_json()

    if not data or not all(key in data for key in ['name', 'price', 'stock']):
        return jsonify({
            "error": "Please provide name, price and stock"
        }), 400

    try:
        name = data['name']
        price = float(data['price'])
        stock = int(data['stock'])

        if not name.strip() or price < 0 or stock < 0:
            return jsonify({
                "error": "Name must not be empty and price and stock must be non-negative"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid price or stock value"
        }), 400

    connection = get_db_connection()

    product = connection.execute(
        'SELECT * FROM products WHERE id = ?',
        (product_id,)
    ).fetchone()

    if product is None:
        connection.close()
        return jsonify({
            "error": "Product not found"
        }), 404

    connection.execute(
        'UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?',
        (name.strip(), price, stock, product_id)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Product updated successfully"
    }), 200


# Delete Product API
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):

    connection = get_db_connection()

    product = connection.execute(
        'SELECT * FROM products WHERE id = ?',
        (product_id,)
    ).fetchone()

    if product is None:
        connection.close()
        return jsonify({
            "error": "Product not found"
        }), 404

    connection.execute(
        'DELETE FROM products WHERE id = ?',
        (product_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Product deleted successfully"
    }), 200



# Start the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
