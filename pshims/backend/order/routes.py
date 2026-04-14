from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required
from webargs.flaskparser import use_args
from backend.order.service import order_service
from backend.common.exceptions import InvalidUsageError, DuplicateResourceError, ResourceNotFoundError
from backend.common.response import response_data
from backend.order.schema import (
    order_create_schema, 
    order_update_schema, 
    order_list_query_args, 
    order_schema, 
    order_list_schema
)
from backend.common.jwt_util import require_permissions
import mimetypes
import os
import re

def get_file_mimetype(file_path):
    """
    根据文件路径获取 MIME 类型
    :param file_path: 文件路径
    :return: MIME 类型字符串
    """
    mimetype, _ = mimetypes.guess_type(file_path)
    return mimetype or 'application/octet-stream'


# 创建订单蓝图
order_bp = Blueprint('order', __name__, url_prefix='/api/orders')

@order_bp.route('', methods=['POST'])
@jwt_required()
@use_args(order_create_schema, location="json")
@require_permissions('OrderManagement')
def create_order(args):
    """新增订单接口"""
    try:
        # args 已经是经过 schema 验证和处理的干净数据
        new_order = order_service.create_order(args)
        # 使用 order_schema 返回完整的订单信息
        return response_data(data=new_order, schema=order_schema), 201
    except DuplicateResourceError as e:
        # 当 service 层抛出此异常时，我们知道是订单号或料号冲突
        raise e
    except Exception as e:
        # 捕获任何其他未知异常
        current_app.logger.error(f"创建订单时发生错误: {e}")
        raise InvalidUsageError(f"创建订单时发生错误: {e}")

@order_bp.route('', methods=['GET'])
@jwt_required()
@use_args(order_list_query_args, location="query")
def get_orders(args):
    """获取订单列表（支持筛选、排序和分页）"""
    try:
        # 从参数中提取分页信息
        page = args['page']
        per_page = args['per_page']
        
        # 提取筛选条件（移除分页和排序参数）
        filter_params = {k: v for k, v in args.items() 
                        if k not in ['page', 'per_page', 'sort_by', 'sort_order'] and v is not None}
        
        # 提取排序信息
        sort_by = args.get('sort_by')
        sort_order = args.get('sort_order')
        
        # 调用服务层获取筛选、排序后的分页数据
        paged_orders = order_service.get_paged_orders(page, per_page, filter_params, sort_by, sort_order)
        
        # 使用 order_list_schema 返回简化的订单信息（包含组件数量）
        return response_data(data=paged_orders, schema=order_list_schema)
    except Exception as e:
        current_app.logger.error(f"获取订单列表时发生错误: {e}")
        raise InvalidUsageError(f"获取订单列表时发生错误: {e}")

@order_bp.route('/<string:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """获取订单详细信息"""
    try:
        order = order_service.get_order_details(order_id)
        # 使用 order_schema 返回完整的订单信息
        return response_data(data=order, schema=order_schema)
    except ResourceNotFoundError as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"获取订单详情时发生错误: {e}")
        raise InvalidUsageError(f"获取订单详情时发生错误: {e}")

@order_bp.route('/<string:order_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@use_args(order_update_schema, location="json")
@require_permissions('OrderManagement')
def update_order(args, order_id):
    """更新订单信息"""
    try:
        # args 就是经过 order_update_schema 验证和处理后的数据
        updated_order = order_service.update_order(order_id, args)
        # 使用 order_schema 来序列化返回的数据
        return response_data(data=updated_order, schema=order_schema)
    except ResourceNotFoundError as e:
        raise e
    except DuplicateResourceError as e:
        raise e
    except Exception as e:
        # 捕获其他可能的未知错误
        current_app.logger.error(f"更新订单时发生错误: {e}")
        raise InvalidUsageError(f"更新订单时发生错误: {e}")

@order_bp.route('/<string:order_id>', methods=['DELETE'])
@jwt_required()
@require_permissions('OrderManagement')
def delete_order(order_id):
    """删除订单（逻辑删除）"""
    try:
        order_service.delete_order(order_id)
        # 对于成功的 DELETE 操作，返回确认消息
        return jsonify({"message": "订单删除成功"}), 200
    except ResourceNotFoundError as e:
        raise e
    except Exception as e:
        # 捕获其他可能的未知错误，并记录日志
        current_app.logger.error(f"删除订单时发生错误: {e}")
        raise InvalidUsageError(f"删除订单时发生错误: {e}")


@order_bp.route('/<order_id>/upload', methods=['POST'])
@jwt_required()
@require_permissions('OrderManagement')
def upload_order_file(order_id):
    """为订单上传附件"""
    try:
        # 检查请求中是否包含文件
        if 'file' not in request.files:
            raise InvalidUsageError("请求中未包含文件")
        
        file = request.files['file']
        
        # 调用service层处理文件上传
        result = order_service.handle_file_upload(
            order_id=order_id,
            file=file,
            upload_folder=current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=current_app.config['ALLOWED_EXTENSIONS']
        )
        
        return jsonify(result), 200
            
    except (ResourceNotFoundError, InvalidUsageError) as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"上传文件时发生错误: {e}")
        raise InvalidUsageError(f"上传文件时发生错误: {e}")


@order_bp.route('/<order_id>/download')
@jwt_required()
def download_order_file(order_id):
    """下载订单附件"""
    try:
        # 调用service层处理文件下载
        file_path, download_filename = order_service.handle_file_download(
            order_id=order_id,
            upload_folder=current_app.config['UPLOAD_FOLDER']
        )
        
        # 记录原始文件名用于日志
        current_app.logger.info(f"下载文件: {download_filename}")
        
        # 创建响应对象
        response = send_file(
            file_path, 
            as_attachment=True, 
            download_name=download_filename,
            mimetype=get_file_mimetype(file_path)
        )
        
        # 添加 CORS 头，允许前端读取 Content-Disposition
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response

        
    except (ResourceNotFoundError, InvalidUsageError) as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"下载文件时发生错误: {e}")
        raise InvalidUsageError(f"下载文件时发生错误: {e}")


@order_bp.route('/softwares/<software_id>/upload', methods=['POST'])
@jwt_required()
@require_permissions('OrderManagement')
def upload_software_file(software_id):
    """为软件上传附件"""
    try:
        # 检查请求中是否包含文件
        if 'file' not in request.files:
            raise InvalidUsageError("请求中未包含文件")
        
        file = request.files['file']
        
        # 调用service层处理文件上传
        result = order_service.handle_software_file_upload(
            software_id=software_id,
            file=file,
            upload_folder=current_app.config['SOFTWARE_UPLOAD_FOLDER'],
            allowed_extensions=current_app.config['ALLOWED_EXTENSIONS']
        )
        
        return jsonify(result), 200
            
    except (ResourceNotFoundError, InvalidUsageError) as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"上传软件文件时发生错误: {e}")
        raise InvalidUsageError(f"上传软件文件时发生错误: {e}")


@order_bp.route('/softwares/<software_id>/download')
@jwt_required()
def download_software_file(software_id):
    """下载软件附件"""
    try:
        # 调用service层处理文件下载
        file_path, download_filename = order_service.handle_software_file_download(
            software_id=software_id,
            upload_folder=current_app.config['SOFTWARE_UPLOAD_FOLDER']
        )
        
        # 记录原始文件名用于日志
        current_app.logger.info(f"下载软件文件: {download_filename}")
        
        # 创建响应对象
        response = send_file(
            file_path, 
            as_attachment=True, 
            download_name=download_filename,
            mimetype=get_file_mimetype(file_path)
        )
        
        # 添加 CORS 头，允许前端读取 Content-Disposition
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response

        
    except (ResourceNotFoundError, InvalidUsageError) as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"下载软件文件时发生错误: {e}")
        raise InvalidUsageError(f"下载软件文件时发生错误: {e}")


@order_bp.route('/export', methods=['GET'])
@jwt_required()
@use_args(order_list_query_args, location="query")
@require_permissions('OrderManagement')
def export_orders(args):
    """
    导出订单数据为Excel文件
    支持与获取订单列表相同的筛选和排序参数
    """
    try:
        # 提取筛选条件（移除分页参数）
        filter_params = {k: v for k, v in args.items() 
                         if k not in ['page', 'per_page'] and v is not None}
        
        # 提取排序信息
        sort_by = args.get('sort_by')
        sort_order = args.get('sort_order')
        
        # 获取所有符合条件的订单（不分页）
        orders = order_service.get_all_orders_for_export(filter_params, sort_by, sort_order)
        
        # 生成Excel文件
        from backend.common.excel import create_order_excel_file, generate_filename
        excel_buffer = create_order_excel_file(orders)
        
        # 生成文件名
        filename = generate_filename("order_export")
        
        # 返回Excel文件
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"导出订单Excel时发生错误: {e}")
        return jsonify({'error': '导出失败'}), 500


@order_bp.route('/import', methods=['POST'])
@jwt_required()
@require_permissions('OrderManagement')
def import_orders():
    """
    批量导入订单
    """
    try:
        if 'file' not in request.files:
            raise InvalidUsageError("请上传文件")
        
        file = request.files['file']
        if not file.filename:
            raise InvalidUsageError("文件名不能为空")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise InvalidUsageError("请上传 Excel 文件（.xlsx 或 .xls）")
        
        # 调用服务层处理导入
        result = order_service.batch_import_orders(file.stream)
        
        # 如果有错误，返回错误 Excel
        if result['error_excel']:
            from datetime import datetime
            filename = f"order_import_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            return send_file(
                result['error_excel'],
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        else:
            # 全部成功
            return jsonify({
                'message': '导入成功',
                'success_count': result['success_count']
            }), 200
            
    except InvalidUsageError as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"导入订单时发生错误: {e}")
        raise InvalidUsageError(f"导入失败: {str(e)}")


@order_bp.route('/import/template', methods=['GET'])
@jwt_required()
def download_import_template():
    """
    下载导入模板
    """
    try:
        from backend.common.excel import create_template_excel
        
        template_buffer = create_template_excel()
        
        return send_file(
            template_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='order_import_template.xlsx'
        )
        
    except Exception as e:
        current_app.logger.error(f"下载模板时发生错误: {e}")
        return jsonify({'error': '下载失败'}), 500
