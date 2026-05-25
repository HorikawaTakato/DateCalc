FROM nginx:1.27-alpine

# デフォルトの nginx.conf を削除して独自の設定に置き換える
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
