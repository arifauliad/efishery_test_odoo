import json
from odoo import http, _
from odoo.http import request, Response

class ApiSaleOrder(http.Controller):
    def unauthorized_response(self):
        return '401 Unauthorized', 'Unauthorized Token'

    def get_order_details(self, order_id):
        request.env.cr.execute('''
            SELECT 
                so.id as order_id,
                so.name as so_name,
                so.date_order so_date_order, 
                so.company_id as company_id,
                rc.name as company_name,
                so.partner_id as partner_id,
                rp.name as partner_name,
                rp.street as partner_address
            FROM sale_order so 
            JOIN res_company rc ON so.company_id = rc.id
            JOIN res_partner rp ON so.partner_id = rp.id
            WHERE 
                so.id IN (%s)
        ''' %(order_id))
        sale_order = request.env.cr.dictfetchone()

        request.env.cr.execute('''
            SELECT 
                sol.price_unit as price_unit,
                pp.id as product_id,
                pt.name as product_name,
                pt.description as pt_description,
                sol.product_uom_qty as qty, 
                sol.product_uom as uom_id,
                uom.name as uom_name,
                uc.name as uom_description
            FROM sale_order_line sol
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN uom_uom uom ON sol.product_uom = uom.id
            JOIN uom_category uc ON uom.category_id = uc.id
            WHERE 
                sol.order_id IN (%s)
        '''% (order_id))
        sale_order_line = request.env.cr.dictfetchall()

        if sale_order:
            order_line = []
            product = []
            uom = []
            for each in sale_order_line:
                order_line.append({
                    "product_id": each.get('product_id'),
                    "product_uom_qty": each.get('qty'),
                    "product_uom": each.get('uom'),
                    "price_unit": each.get('price_unit')
                })
                product.append({
                    "id": each.get('product_id'),
                    "name": each.get('product_name'),
                    "description": each.get('pt_description'),
                    "price": each.get('price_unit'),
                })
                uom.append({
                    "id": each.get('uom_id'),
                    "name": each.get('uom_name'),
                    "description": each.get('uom_description'),
                })

            data = {
                "name": sale_order.get('so_name'),
                "partner_id": sale_order.get('partner_id'),
                "date_order": str(sale_order.get('so_date_order')),
                "company_id": sale_order.get('company_id'),
                "partner": [
                    {
                        "partner_id": sale_order.get('partner_id'),
                        "name": sale_order.get('partner_name'),
                        "address": sale_order.get('partner_address'),
                    }
                ],
                "product": product,
                "company": [
                    {
                        "id": sale_order.get('company_id'),
                        "name": sale_order.get('company_name'),
                        "description": "The company"
                    }
                ],
                "uom": uom,
                "order_line": order_line
            }
            return data
        else:
            return False

    def make_get_response(self, order_id):
        data = {}
        success_status = False
        get_order_details = self.get_order_details(int(order_id))
        if get_order_details:
            success_status = True
            response_status = "200 OK"
            response_message = "Data found"
            data = get_order_details
        else:
            response_status = "400 Bad request"
            response_message = "Order Id Not Found"

        return {
            'response_status': response_status,
            'response_message': response_message,
            'success_status': success_status,
            'data': data
        }

    @http.route('/api/order/<order_id>', auth='public', methods=['GET'])
    def get_sale_order_one(self, order_id=0):
        data = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('default.static_token'))
        headers = http.request.httprequest.headers
        if headers.get('Authorization') == access_token:
            if not order_id:
                response_status = "400 Bad request"
                response_message = "No Order Id Sent"
            else:
                check_order_details = self.make_get_response(order_id)
                response_status = check_order_details['response_status']
                response_message = check_order_details['response_message']
                success_status = check_order_details['success_status']
                data = check_order_details['data']
        else:
            response_status, response_message = self.unauthorized_response()

        result = {
            "success": success_status,
            "message": response_message,
            "data": data
        }
        return Response(json.dumps(result), headers=headers_json, status=response_status)

    def make_data_response(self, sale_order):
        result = {
            'so_id': sale_order.id,
            'partner_id': sale_order.partner_id.id,
            'date_order': str(sale_order.date_order),
            'sale_order_name': sale_order.sale_order_name,
            'company_id': sale_order.company_id.id,
            'order_line': [{
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit
            } for line in sale_order.order_line]
        }

        return result

    def check_payload(self, request_order):
        if not request_order.get('partner_id') or not request_order.get('date_order') or not request_order.get('company_id') or not request_order.get('order_line'):
            return 'Payload Error or Some Required Field not Fill Yet'

        if request_order.get('partner_id'):
            if not request.env['res.partner'].sudo().search([('id','=',request_order.get('partner_id'))]):
                return 'Partner Not found'
        return 'OK'

    @http.route('/api/order', auth='public', csrf=False, methods=['POST'])
    def create_sale_order(self):
        data_order = json.loads((request.httprequest.data).decode())
        data_response = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('default.static_token'))
        headers = http.request.httprequest.headers
        if headers.get('Authorization') == access_token:
            if data_order:
                check_result = self.check_payload(data_order)
                if check_result != 'OK':
                    response_status = "400 Bad Request"
                    response_message = check_result
                else:
                    exist_sale_order = request.env['sale.order'].sudo().search([('sale_order_name','=',data_order.get('name'))], limit=1)

                    if exist_sale_order:
                        response_status = "400 Bad Request"
                        response_message = "Sales Order Already Exist"
                    else:
                        order_lines = [(0, 0, {
                            'product_id': line['product_id'],
                            'product_uom_qty': line['product_uom_qty'],
                            'product_uom': line['product_uom'],
                            'price_unit': line['price_unit']
                        }) for line in data_order.get('order_line')]

                        sale_order = request.env['sale.order'].sudo().create({
                            'partner_id': data_order.get('partner_id'),
                            'date_order': data_order.get('date_order'),
                            'sale_order_name': data_order.get('name'),
                            'company_id': data_order.get('company_id'),
                            'order_line': order_lines
                        })

                        success_status = True
                        response_status = "200 OK"
                        response_message = "Sales order created"
                        data_response = self.make_data_response(sale_order)
            else:
                response_status = "400 Bad Request"
                response_message = "Payload Request is empty"
        else:
            response_status, response_message = self.unauthorized_response()

        result = {
            "success": success_status,
            "message": response_message,
            "data": data_response
        }
        return Response(json.dumps(result), headers=headers_json, status=response_status)

    @http.route('/api/order/<order_id>', auth='public', csrf=False, methods=['PUT'])
    def update_sale_order(self, order_id=0):
        data_order = json.loads((request.httprequest.data).decode())
        data_response = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('default.static_token'))
        headers = http.request.httprequest.headers
        if headers.get('Authorization') == access_token:
            if data_order:
                check_result = self.check_payload(data_order)
                if check_result != 'OK':
                    response_status = "400 Bad Request"
                    response_message = check_result
                else:
                    sale_order = request.env['sale.order'].sudo().search([('id','=',int(order_id))])
                    if not sale_order:
                        response_status = "400 Bad Request"
                        response_message = "Sales Order not Found"
                    elif sale_order.state != "draft":
                        response_status = "400 Bad Request"
                        response_message = "Sales Order not In Draft State"
                    else:
                        new_line = []
                        delete_line = []
                        save_line = []
                        for update_line in data_order.get('order_line'):
                            existing_product = sale_order.order_line.filtered(lambda x: x.product_id.id == update_line['product_id'])
                            if existing_product:
                                if existing_product.price_unit != update_line['price_unit'] or existing_product.product_uom_qty != update_line['product_uom_qty']:
                                    existing_product.price_unit = update_line['price_unit']
                                    existing_product.product_uom_qty = update_line['product_uom_qty']
                            else:
                                new_line.append((0, 0, {
                                    'product_id': update_line['product_id'],
                                    'product_uom': update_line['product_uom'],
                                    'product_uom_qty': update_line['product_uom_qty'],
                                    'price_unit': update_line['price_unit']
                                }))

                        sale_order.sudo().write({
                            'partner_id': data_order.get('partner_id'),
                            'sale_order_name': data_order.get('sale_order_name'),
                            'date_order': data_order.get('date_order'),
                            'order_line': new_line
                        })

                        for update_line in data_order.get('order_line'):
                            existing_product = sale_order.order_line.filtered(lambda x: x.product_id.id == update_line['product_id'])
                            if existing_product:
                                save_line.append(existing_product.id)

                        for line in sale_order.order_line:
                            if line.id not in save_line:
                                delete_line.append((2, line.id))

                        sale_order.order_line = delete_line

                        success_status = True
                        response_status = "200 OK"
                        response_message = "Sales order updated"
                        data_response = self.make_data_response(sale_order)
            else:
                response_status = "400 Bad Request"
                response_message = "Payload Request is empty"
        else:
            response_status, response_message = self.unauthorized_response()

        result = {
            "success": success_status,
            "message": response_message,
            "data": data_response
        }
        return Response(json.dumps(result), headers=headers_json, status=response_status)