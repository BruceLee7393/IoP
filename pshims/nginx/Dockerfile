# (这是我们之前写的 nginx/Dockerfile)

# 第1行: FROM nginx:alpine
# 意思：告诉 Docker，我们的定制工作要从“nginx:alpine”这个官方的、
# 轻量级的纯净镜像开始。就像画画前先准备一张干净的白纸。
FROM nginx:alpine

# 第2行: COPY app.conf /etc/nginx/conf.d/app.conf
# 意思：将我们项目目录中 nginx 文件夹下的 app.conf 文件，
# 复制到镜像内部的 /etc/nginx/conf.d/ 目录下，并命名为 app.conf。
# 
# 为什么是这个目录？
# 因为官方 Nginx 镜像被设计为会自动加载这个目录里所有以 .conf 结尾的配置文件。
# 所以，把我们的配置放进去，Nginx 启动时就会自动使用它。
COPY nginx/app.conf /etc/nginx/conf.d/app.conf

# 第3行: RUN rm /etc/nginx/conf.d/default.conf
# 意思：执行一个删除命令，把镜像里原来就存在的默认配置文件 default.conf 给删掉。
# 
# 为什么要删？
# 这是一个好习惯，可以防止默认配置和我们的 app.conf 发生冲突。
# 我们只想让 Nginx 100% 听我们 app.conf 的指挥。
RUN rm /etc/nginx/conf.d/default.conf

# 第4行: COPY ../frontend_dist /var/www/frontend
# 意思：将我们项目目录中 nginx 文件夹的上一级目录（../）里的 frontend_dist 文件夹，
# 整个复制到镜像内部的 /var/www/frontend 目录下。
#
# 为什么要这样做？
# 这步至关重要！你的 app.conf 里写了 `root /var/www/frontend;`。
# 这行配置告诉 Nginx：“当有浏览器请求网页时，请到容器的 /var/www/frontend 目录里去找对应的文件（比如 index.html）”。
# 如果我们不把前端文件复制到这个位置，Nginx 就会因为找不到文件而返回 404 Not Found 错误。
# 这一步操作，就是把“弹药”（前端文件）装填到“炮台”（Nginx）里。
COPY ./dist /var/www/frontend
