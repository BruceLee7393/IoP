from backend.order import dao
from backend.common.exceptions import DuplicateResourceError, ResourceNotFoundError, InvalidUsageError
import os
class OrderService:
    """订单服务类，处理与订单相关的业务逻辑"""

    def create_order(self, order_data):
        """
        创建新订单
        :param order_data: 包含订单信息和组件数据的字典
        :return: 创建的Order对象
        :raises DuplicateResourceError: 如果订单号或料号已存在
        """
        # 1. 检查订单号是否已存在
        if dao.check_order_number_exists(order_data['order_number']):
            raise DuplicateResourceError(f"订单号 '{order_data['order_number']}' 已存在。")
        
        
        # 2. 调用DAO创建订单
        new_order = dao.add_order(order_data)
        return new_order

    def get_paged_orders(self, page, per_page, filter_params=None, sort_by=None, sort_order='desc'):
        """
        获取分页的订单列表，支持筛选和排序
        :param page: 页码
        :param per_page: 每页数量
        :param filter_params: 筛选条件字典
        :param sort_by: 排序字段
        :param sort_order: 排序方向 ('asc' 或 'desc')
        :return: SQLAlchemy Pagination 对象
        """
        # 调用DAO层获取筛选、排序后的分页对象
        pagination = dao.get_all_orders(page, per_page, filter_params, sort_by, sort_order)
        return pagination

    def get_order_by_id(self, order_id):
        """
        根据ID获取订单详细信息
        :param order_id: 订单ID
        :return: Order对象
        :raises ResourceNotFoundError: 如果订单不存在
        """
        order = dao.get_order_by_id(order_id)
        if not order:
            raise ResourceNotFoundError(f"ID为 '{order_id}' 的订单不存在。")
        return order

    def update_order(self, order_id, update_data):
        """
        更新订单信息
        :param order_id: 要更新的订单ID
        :param update_data: 包含要更新字段的字典，若含 components 则进行整棵子树替换
        :return: 更新后的Order对象
        :raises ResourceNotFoundError: 如果订单ID不存在
        :raises DuplicateResourceError: 如果更新后的订单号与其他订单冲突
        """
        # 1. 根据ID查找订单
        order_to_update = dao.get_order_by_id(order_id)
        if not order_to_update:
            raise ResourceNotFoundError(f"ID为 '{order_id}' 的订单不存在。")
        
        # 2. 检查订单号是否与其他订单冲突（如果更新了订单号）
        if 'order_number' in update_data and update_data['order_number'] != order_to_update.order_number:
            if dao.check_order_number_exists(update_data['order_number'], exclude_id=order_id):
                raise DuplicateResourceError(f"订单号 '{update_data['order_number']}' 已被其他订单使用。")


        
        # 3. 调用DAO层执行更新（支持子树替换）
        updated_order = dao.update_order(order_to_update, update_data)
        return updated_order

    def delete_order(self, order_id):
        """
        物理删除订单
        :param order_id: 要删除的订单ID
        :raises ResourceNotFoundError: 如果订单ID不存在
        """
        order_to_delete = dao.get_order_by_id(order_id)
        if not order_to_delete:
            raise ResourceNotFoundError(f"ID为 '{order_id}' 的订单不存在。")
        
        dao.delete_order(order_to_delete)

    def get_order_details(self, order_id):
        """
        获取订单详细信息，包含所有关联的组件、子组件和软件
        :param order_id: 订单ID
        :return: 包含完整信息的Order对象
        :raises ResourceNotFoundError: 如果订单不存在
        """
        order = dao.get_order_with_details(order_id)
        if not order:
            raise ResourceNotFoundError(f"ID为 '{order_id}' 的订单不存在。")
        return order

    def update_order_appendix(self, order_id, appendix_url):
        """
        更新订单的附件地址
        :param order_id: 订单ID
        :param appendix_url: 附件下载地址
        :return: 更新后的订单对象
        :raises ResourceNotFoundError: 如果订单不存在
        """
        order = dao.get_order_by_id(order_id)
        if not order:
            raise ResourceNotFoundError(f"ID为 '{order_id}' 的订单不存在。")
        
        # 更新附件字段
        update_data = {'appendix': appendix_url}
        updated_order = dao.update_order(order, update_data)
        return updated_order

    def handle_file_upload(self, order_id, file, upload_folder, allowed_extensions):
        """
        处理文件上传逻辑
        :param order_id: 订单ID
        :param file: 上传的文件对象
        :param upload_folder: 上传目录
        :param allowed_extensions: 允许的文件扩展名集合
        :return: 上传结果字典
        :raises InvalidUsageError: 各种验证失败
        :raises ResourceNotFoundError: 订单不存在
        :raises InvalidUsageError: 文件过大
        """
        import os
        
        # 检查订单是否存在
        order = dao.get_order_by_id(order_id)
        if not order:
            raise ResourceNotFoundError(f"订单ID '{order_id}' 不存在")
        
        # 检查文件是否为空
        if not file or file.filename == '':
            raise InvalidUsageError("未选择文件")
        
        # 检查文件大小是否超过1GB
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > 1024 * 1024 * 1024:
            raise InvalidUsageError("上传文件过大，禁止上传（超过1GB）")
        
        # 检查文件类型
        if not self._is_allowed_file(file.filename, allowed_extensions):
            raise InvalidUsageError("不允许的文件类型，只支持: " + ', '.join(allowed_extensions))
        
        # 获取文件扩展名和原始文件名
        original_filename = file.filename
        if '.' in original_filename:
            file_extension = original_filename.rsplit('.', 1)[1].lower()
        else:
            raise InvalidUsageError("文件名必须包含扩展名")
        
        # 服务器存储使用订单ID作为文件名
        server_filename = f"{order_id}.{file_extension}"
        
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 删除旧文件
        self._remove_old_attachment(order_id, upload_folder)
        
        # 保存新文件（服务器用ID命名）
        file_path = os.path.join(upload_folder, server_filename)
        file.save(file_path)
        
        # 更新订单的附件字段（存储原始文件名）
        self.update_order_appendix(order_id, original_filename)
        
        return {
            'message': '文件上传成功',
            'filename': server_filename,
            'original_filename': original_filename,
            'order_id': order_id
        }

    def handle_file_download(self, order_id, upload_folder):
        """
        处理文件下载逻辑
        :param order_id: 订单ID
        :param upload_folder: 上传目录
        :return: (文件路径, 下载文件名) 元组
        :raises ResourceNotFoundError: 订单不存在或文件不存在
        :raises InvalidUsageError: 订单没有附件
        """
        
        # 检查订单是否存在并获取附件信息
        order = dao.get_order_by_id(order_id)
        if not order:
            raise ResourceNotFoundError(f"订单ID '{order_id}' 不存在")
        
        # 检查订单是否有附件
        if not order.appendix:
            raise InvalidUsageError("该订单没有附件")
        
        # 获取原始文件名
        original_filename = order.appendix
        
        # 验证原始文件名格式
        if not original_filename or original_filename.strip() == '':
            raise InvalidUsageError("附件文件名为空")
        
        # 从原始文件名获取扩展名
        if '.' in original_filename:
            file_extension = original_filename.rsplit('.', 1)[1].lower()
        else:
            raise InvalidUsageError("附件文件名格式错误，缺少扩展名")
        
        # 构建服务器文件路径（使用ID命名）
        server_filename = f"{order_id}.{file_extension}"
        file_path = os.path.join(upload_folder, server_filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ResourceNotFoundError("附件文件不存在")
        
        # 下载文件名使用原始文件名，确保编码正确
        download_filename = original_filename
        
        return file_path, download_filename

    def handle_software_file_upload(self, software_id, file, upload_folder, allowed_extensions):
        """
        处理软件文件上传逻辑
        :param software_id: 软件ID
        :param file: 上传的文件对象
        :param upload_folder: 上传目录
        :param allowed_extensions: 允许的文件扩展名集合
        :return: 上传结果字典
        :raises InvalidUsageError: 各种验证失败
        :raises ResourceNotFoundError: 软件不存在
        :raises InvalidUsageError: 文件过大
        """
        import os
        
        # 检查软件是否存在
        software = dao.get_software_by_id(software_id)
        if not software:
            raise ResourceNotFoundError(f"软件ID '{software_id}' 不存在")
        
        # 检查文件是否为空
        if not file or file.filename == '':
            raise InvalidUsageError("未选择文件")
        
        # 检查文件大小是否超过1GB
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > 1024 * 1024 * 1024:
            raise InvalidUsageError("上传文件过大，禁止上传（超过1GB）")
        
        # 检查文件类型
        if not self._is_allowed_file(file.filename, allowed_extensions):
            raise InvalidUsageError("不允许的文件类型，只支持: " + ', '.join(allowed_extensions))
        
        # 获取文件扩展名和原始文件名
        original_filename = file.filename
        if '.' in original_filename:
            file_extension = original_filename.rsplit('.', 1)[1].lower()
        else:
            raise InvalidUsageError("文件名必须包含扩展名")
        
        # 服务器存储使用软件ID作为文件名
        server_filename = f"{software_id}.{file_extension}"
        
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 删除旧文件
        self._remove_old_software_attachment(software_id, upload_folder)
        
        # 保存新文件（服务器用ID命名）
        file_path = os.path.join(upload_folder, server_filename)
        file.save(file_path)
        
        # 更新软件的附件字段（存储原始文件名）
        self.update_software_appendix(software_id, original_filename)
        
        return {
            'message': '软件文件上传成功',
            'filename': server_filename,
            'original_filename': original_filename,
            'software_id': software_id
        }

    def handle_software_file_download(self, software_id, upload_folder):
        """
        处理软件文件下载逻辑
        :param software_id: 软件ID
        :param upload_folder: 上传目录
        :return: (文件路径, 下载文件名) 元组
        :raises ResourceNotFoundError: 软件不存在或文件不存在
        :raises InvalidUsageError: 软件没有附件
        """

        
        # 检查软件是否存在并获取附件信息
        software = dao.get_software_by_id(software_id)
        if not software:
            raise ResourceNotFoundError(f"软件ID '{software_id}' 不存在")
        
        # 检查软件是否有附件
        if not software.appendix:
            raise InvalidUsageError("该软件没有附件")
        
        # 获取原始文件名
        original_filename = software.appendix
        
        # 验证原始文件名格式
        if not original_filename or original_filename.strip() == '':
            raise InvalidUsageError("附件文件名为空")
        
        # 从原始文件名获取扩展名
        if '.' in original_filename:
            file_extension = original_filename.rsplit('.', 1)[1].lower()
        else:
            raise InvalidUsageError("附件文件名格式错误，缺少扩展名")
        
        # 构建服务器文件路径（使用ID命名）
        server_filename = f"{software_id}.{file_extension}"
        file_path = os.path.join(upload_folder, server_filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ResourceNotFoundError("附件文件不存在")
        
        # 下载文件名使用原始文件名，确保编码正确
        download_filename = original_filename
        
        return file_path, download_filename

    def get_software_by_id(self, software_id):
        """
        根据ID获取软件信息
        :param software_id: 软件ID
        :return: Software对象或None
        """
        return dao.get_software_by_id(software_id)

    def update_software_appendix(self, software_id, appendix_url):
        """
        更新软件的附件地址
        :param software_id: 软件ID
        :param appendix_url: 附件下载地址
        :return: 更新后的软件对象
        :raises ResourceNotFoundError: 如果软件不存在
        """
        software = dao.get_software_by_id(software_id)
        if not software:
            raise ResourceNotFoundError(f"ID为 '{software_id}' 的软件不存在。")
        
        software.appendix = appendix_url
        dao.update_software(software)
        return software

    def _is_allowed_file(self, filename, allowed_extensions):
        """检查文件扩展名是否允许"""
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in allowed_extensions

    def _remove_old_attachment(self, order_id, upload_folder):
        """删除订单的旧附件文件"""
        import os
        from flask import current_app
        
        try:
            for existing_file in os.listdir(upload_folder):
                if existing_file.startswith(f"{order_id}."):
                    old_file_path = os.path.join(upload_folder, existing_file)
                    try:
                        os.remove(old_file_path)
                        current_app.logger.info(f"删除旧附件文件: {existing_file}")
                    except OSError as e:
                        current_app.logger.warning(f"删除旧文件失败: {e}")
        except OSError:
            # 目录不存在或其他错误，忽略
            pass

    def _remove_old_software_attachment(self, software_id, upload_folder):
        """删除软件的旧附件文件"""
        import os
        from flask import current_app
        
        try:
            for existing_file in os.listdir(upload_folder):
                if existing_file.startswith(f"{software_id}."):
                    old_file_path = os.path.join(upload_folder, existing_file)
                    try:
                        os.remove(old_file_path)
                        current_app.logger.info(f"删除旧软件文件: {existing_file}")
                    except OSError as e:
                        current_app.logger.warning(f"删除旧软件文件失败: {e}")
        except OSError:
            # 目录不存在或其他错误，忽略
            pass

    def get_all_orders_for_export(self, filter_params=None, sort_by=None, sort_order='desc'):
        """
        获取所有符合条件的订单用于导出，支持筛选和排序
        :param filter_params: 筛选条件字典
        :param sort_by: 排序字段
        :param sort_order: 排序方向 ('asc' 或 'desc')
        :return: 订单列表
        """
        # 调用DAO层获取所有符合条件的订单
        orders = dao.get_all_orders_for_export(filter_params, sort_by, sort_order)
        return orders

    def batch_import_orders(self, file_stream):
        """
        批量导入订单
        :param file_stream: Excel 文件流
        :return: {'success_count': int, 'error_count': int, 'error_excel': BytesIO or None}
        """
        from backend.common.excel import parse_order_excel, create_error_excel
        
        # 1. 解析 Excel
        success_orders, error_orders = parse_order_excel(file_stream)
        
        # 2. 导入成功的订单
        imported_count = 0
        import_errors = []
        
        for order_data in success_orders:
            try:
                # 检查订单号是否已存在
                if dao.check_order_number_exists(order_data['order_number']):
                    import_errors.append({
                        'order': order_data,
                        'error': f"订单号 '{order_data['order_number']}' 已存在"
                    })
                    continue
                
                # 创建订单
                dao.add_order(order_data)
                imported_count += 1
                
            except Exception as e:
                import_errors.append({
                    'order': order_data,
                    'error': str(e)
                })
        
        # 3. 合并所有错误（验证错误 + 导入错误）
        all_errors = error_orders + import_errors
        
        # 4. 生成错误 Excel（如果有错误）
        error_excel = None
        if all_errors:
            error_excel = create_error_excel(all_errors)
        
        return {
            'success_count': imported_count,
            'error_count': len(all_errors),
            'error_excel': error_excel
        }

# 创建一个服务实例，方便其他地方调用
order_service = OrderService()
