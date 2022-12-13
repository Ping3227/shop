# 資料庫系統期末專案
### 姓名：施開嚴(R10525133)、黃緯翔(B09204045)


## 一、開啟程式
1. 首先使用Visual Studio Code這個APP開啟名為【final_dbms】的資料夾
   

2. 按下右上角的Debug模式執行程式
   
3. 可以獲得本地端的網址 http://127.0.0.1:5000/
![執行畫面](/image/1.JPG)
![Home](/image/2.JPG)


## 二、User功能介紹

### 2.1 建立買家、賣家帳號
1. 使用 http://127.0.0.1:5000/api/users 的POST功能，來新增使用者
![registerPage](/image/3.JPG)
   
2. 新增買家，輸入相關資訊並且type要打成buyer
3. 新增賣家輸入相關資訊並且type要打成seller

![register](/image/register.JPG)

4. 以下為建立資料庫裡的人員


![userTable](/image/userTable.JPG)  

### 2.2 使用者登入帳號
1. 使用 http://127.0.0.1:5000/api/users/signIn 的POST功能，來登入帳號
![signIn](/image/signIn.JPG)   
2. 輸入信箱與密碼登入成功產生Json Web Token，讓使用者可以一段時間內保有此狀態在接下來的操作
   
![Token](/image/token.JPG)   

### 2.3使用者更改名字或手機號碼
1. 登入後，使用 http://127.0.0.1:5000/api/users/me 的PATCH功能來修改資料
   
2. 可以發現圖中id=1的已成功修改  
   
![patch](/image/patch.JPG)  ![newdata](/image/newdata.JPG)  
   

### 2.4取得自己的資料
   1. 登入後，使用 http://127.0.0.1:5000/api/users/{id} 的GET功能獲得資料

![owndata](/image/userinformation.JPG) 

### 2.5(增)登出帳號
   1. 使用 http://127.0.0.1:5000/api/users/logout 的POST功能刪除cookies中的JWT，以防有心人士使用
      
      

## 三、Product功能介紹

### 3.1賣家新增販賣商品
   1. 登入後，使用 http://127.0.0.1:5000/api/sellers/me/products 的POST功能，輸入相關資訊新增產品
   

### 3.2賣家獲得全部產品資訊
   1. 使用 http://127.0.0.1:5000/api/sellers/me/products 的GET功能，取得全部產品相關資訊
   

### 3.3賣家獲得特定產品資訊
   1. 使用 http://127.0.0.1:5000/api/sellers/{ellerId}/products 的GET功能，取得特定產品資訊
    

### 3.4賣家更新特定產品資訊
   1. 登入後，使用 http://127.0.0.1.5000/api/products/{ProductId} 的PATCH，更新特定產品資訊
   
   

### 3.5賣家刪除掉特定產品(可不用)
   1. 登入後，使用 http://127.0.0.1:5000/api/products/{id} 的DELETE，刪除特定產品資訊
   
     

## 四、Order功能介紹

### 4.1 買家新增訂單
   1. 登入後，使用 http://127.0.0.1:5000/api/buyers/me/orders 的POST，來新增所想訂的訂單
 
 
### 4.2 買家查看訂單
   1. 登入後，使用 http://127.0.0.1:5000/api/buyers/me/orders 的GET，查看自己所下的訂單   
   

### 4.3賣家觀看全部有和他下單的資料
   1. 登入後，使用 http://127.0.0.1:5000/api/sellers/me/orders 的GET，來觀看全部有下單的資料
   

### 4.4買家觀看特定下單的資料
1. 登入後，使用 http://127.0.0.1:5000/api/orders/{orderid} 的GET，來觀看特定下單的資料
   
### 4.5買家更新特定下單的資料
1. 登入後，使用 http://127.0.0.1:5000/api/orders/{orderid} 的GET，來觀看特定下單的資料
