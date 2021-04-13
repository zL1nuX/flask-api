from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

PRODUCTS = [
    {'name': 'chair',
     'price': 5000,
     },
    {'name': 'table',
     'price': 2000
     }
]


def check_item_doesnt_exist(name):
    if not list(filter(lambda x: x['name'] == name, PRODUCTS)):
        abort(404, message=f"Product {name} is not found")


def check_item_existence(name):
    if list(filter(lambda x: x['name'] == name, PRODUCTS)):
        abort(404, message=f"Product {name} already exists")


def check_if_price_was_given(args):
    try:
        if not args['price']:
            abort(400, message='Price was not given')
    except KeyError:
        abort(400, message='Price was not given')


def get_product_by_name(name):
    return list(filter(lambda x: x['name'] == name, PRODUCTS))[0]


@app.route('/')
def index():
    return 'Hello World'


class Item(Resource):
    def get(self, name):
        check_item_doesnt_exist(name)
        return get_product_by_name(name), 200

    def post(self, name):
        check_item_existence(name)
        parser.add_argument('price')
        args = parser.parse_args()
        check_if_price_was_given(args)
        PRODUCTS.append({
            'name': name,
            'price': args['price']
        })
        return PRODUCTS[-1], 201

    def put(self, name):
        parser.add_argument('price')
        args = parser.parse_args()
        check_if_price_was_given(args)
        try:
            product = get_product_by_name(name)
            PRODUCTS[PRODUCTS.index(product)]['price'] = args['price']
            return get_product_by_name(name), 201
        except:
            PRODUCTS.append({'name': name,
                             'price': args['price']})
            return get_product_by_name(name), 201

    def delete(self, name):
        check_item_doesnt_exist(name)
        product = get_product_by_name(name)
        PRODUCTS.pop(PRODUCTS.index(product))
        return None, 204


class ItemList(Resource):
    def get(self):
        return PRODUCTS, 200

    def post(self):
        global PRODUCTS
        parser.add_argument("products", type=dict, action='append')
        args = parser.parse_args()
        if not args:
            abort(400, message="Arguments are incorrect")
        # Separating new products
        clear = []
        for i, item in enumerate(args['products']):
            check_if_price_was_given(item)
            if not list(filter(lambda x: x['name'] == item['name'], PRODUCTS)):
                clear.append(args['products'][i])
        # Check if there is nothing new
        if clear:
            PRODUCTS += clear
            return clear, 200
        else:
            abort(400, message="All of these products already exist")


api.add_resource(Item, '/items/<string:name>')
api.add_resource(ItemList, '/items')

if __name__ == '__main__':
    app.run(debug=True)
