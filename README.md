# efishery_test_odoo
Jalankan command “docker compose up” dan lihat log pada terminal
![Screen Shot 2021-09-07 at 16 21 43](https://user-images.githubusercontent.com/48560951/132320330-94269d22-9e07-4df2-9156-b18115b0c56a.png)

Check interception system dengan ketik “http://localhost:5000/check” pada browser
![Screen Shot 2021-09-07 at 16 21 53](https://user-images.githubusercontent.com/48560951/132320377-26250817-1bfd-44c8-abcb-401ad1d3cdda.png)

Buka url odoo “http://localhost:8069/”, saat pertama akan diarahkan ke halaman pembuatan db 
![Screen Shot 2021-09-07 at 16 22 06](https://user-images.githubusercontent.com/48560951/132320384-38662c8c-bfd2-485a-a6f7-8c35520d984a.png)

Buatlah db dengan:
![Screen Shot 2021-09-07 at 16 22 14](https://user-images.githubusercontent.com/48560951/132320400-34da5f9d-6abb-473a-aa38-82911fb46b7b.png)

Penjelasan:
Master Password : 12345678 (harus dengan password ini karena telah di set di config odoo)
Database name : efishery (harus dengan db dengan nama ini karena pada config di filter hanya untuk nama ini saja, untuk memudahkan juga saat terjadi request dari interception system ke odoo)
Email : (email anda)
Password : 12345678 (sesuai keinginan)
Demo data : check supaya dapat data demo dari odoo

Setelah itu anda akan di redirect ke laman apps odoo. Search module ‘efishery’ dan install
![Screen Shot 2021-09-07 at 16 22 25](https://user-images.githubusercontent.com/48560951/132320408-1f4ab00f-84ab-4946-8ccd-9217d50290df.png)

Setting token pada menu setting - efishery
![Screen Shot 2021-09-07 at 16 22 32](https://user-images.githubusercontent.com/48560951/132320414-c8c6d910-e9d8-476b-9625-94463c26b6a1.png)

Test dengan menggunakan command
curl -X 'GET' 'http://127.0.0.1:5001/order/1' -H 'accept: application/json' -H 'Content-Type: application/json' -H 'Authorization: static_token'
![Screen Shot 2021-09-07 at 16 22 44](https://user-images.githubusercontent.com/48560951/132320422-7c185e35-ed8b-4836-b1df-d9f929901a53.png)

Untuk API yang tersedia
Get 1 Order
Method: GET
Url: host:port/order/{order_id}

Save Order
Method: POST
Url: host:port/order/

Update Order
Method: PUT
Url: host:port/order/{order_id}

Data yang digunakan sesuai dengan yg ada pada soal test
