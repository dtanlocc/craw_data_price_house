# %%
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# %%
file_name = 'link.xlsx'
#read file excel with pandas
df = pd.read_excel(file_name,sheet_name='search')
df['links'] = df['links'].str.replace('.html',f"/page-1.html")
links_seach = df['links']

print(links_seach)

# %%
# Tạo một dataframe mới cho sheet mới
data = {
    'Title': [],  # Thay đổi dữ liệu cho cột Title
    'Link': [],  # Thay đổi dữ liệu cho cột Link
    'Giá': [], 
    'Diện tích': [],
    'Mã tin': [],
    'Mặt tiền': [], 
    'Đường trước nhà': [], 
    'Số tầng': [], 
    'Số phòng': [], 
    'Số toilet': [], 
    'Nội thất': [], 
    'Ngày đăng tin': [], 
    'Ngày hết hạn': []
}
new_sheet_df = pd.DataFrame(data)

# Lưu dataframe mới vào sheet "link" trong file Excel
with pd.ExcelWriter(file_name, engine='openpyxl', mode='a') as writer:
    new_sheet_df.to_excel(writer, sheet_name='link', index=False)

# %%
def get_page_number(link_search):
    html = requests.get(link_search)
    # print(html.text)
    
    s = BeautifulSoup(html.content,'html.parser')
    page = s.find('span','current_page_item')
    page = page.find_all('b')
    
    return int(page[1].get_text())

# %% [markdown]
# # Get price

# %%
def get_price_area(link):
    data = {
    'Title': [],  # Thay đổi dữ liệu cho cột Title
    'Link': [],  # Thay đổi dữ liệu cho cột Link
    'Giá': [], 
    'Diện tích': [],
    'Mã tin': [],
    'Mặt tiền': [], 
    'Đường trước nhà': [], 
    'Số tầng': [], 
    'Số phòng': [], 
    'Số toilet': [], 
    'Nội thất': [], 
    'Ngày đăng tin': [], 
    'Ngày hết hạn': []
    }
    # html = 'https://thongkenhadat.com/ban-nha-rieng-nha-hem-to-hieu-tan-thoi-hoa-14892/nha-ban-to-hieu-tan-phu-9-chdv-hxh-4-tang-60m2-thu-nhap-480trieu.html'
    html = requests.get(link)
    s = BeautifulSoup(html.content,'html.parser')

    #get price
    price = s.find('p','div-price-in').span.get_text()
    try:
        price= price.split(":")[1]
    except:
        price = 'Thỏa thuận'
    data['Giá'].append(price)

    #get_area
    area = s.find('span','span-3').get_text()
    try:
        area = float(re.search(r'\d+\.\d+|\d+', area).group())
    except:
        area = 'Không xác định'
    data['Diện tích'].append(area)
    #get infor
    profile = s.find_all('div','ul-info')
    elements = profile[0].find_all('div','row-line')
    # print(elements[1].find('span','span-2').get_text())
    for element in elements:
        key =element.find('span','span-1').get_text()
        if key in data:
            data[key].append(element.find('span','span-2').get_text())
    return data

# %%
#get_price_area('https://thongkenhadat.com/ban-nha-rieng-nha-hem-nguyen-anh-thu-tan-chanh-hiep-13539/nha-ban-76m2-hem-oto-6mnguyen-anh-thu1-tret-1-laugia-4x-ty.html')

# %%
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
for search in links_seach:
    # search = 'https://thongkenhadat.com/ban-nha-ho-chi-minh-1.html'
    page = get_page_number(search)
    
    
    for page_number in range(1,page+1):
        search = re.sub(r'page-\d+', f'page-{page_number}', search)
        print(search)
        try:
            html = requests.get(search)
            # print(html.text)
            
            s = BeautifulSoup(html.content,'html.parser')
            titles = s.find_all('li','style1')
            i = 0
            for title in titles:
                name = title.find_all('h3','name')
                url = title.find_all('a',href=True)
                link = url[0]['href']
                df_link = pd.read_excel(file_name, sheet_name='link')
                new_data = {
                                'Title': [name[0].get_text()],
                                'Link': [link]
                            }
                data = get_price_area(link)
                # print(data['Title'])
                data['Title'].extend(new_data['Title'])
                data['Link'].extend(new_data['Link'])
                # print(data['Title'])

                data = {k: [None if not v else v] for k, v in data.items()}
                # Tạo DataFrame từ dữ liệu mới
                new_data_df = pd.DataFrame(data)
                for col in new_data_df.columns:
                    new_data_df[col] = new_data_df[col].str[0]

                # print(new_data_df)
                
                # Kết hợp DataFrame mới với DataFrame hiện có
                combined_df = pd.concat([df_link, new_data_df], ignore_index=True)
                
                # Lưu dữ liệu kết hợp vào sheet "link" trong file Excel
                with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    combined_df.to_excel(writer, sheet_name='link', index=False)
                print(f'{i}: Crawl link {link}')
                i+= 1
            print(f'End page {page_number}')

        except:
            print('Eror')
            # links.append(url[0]['href'])
            # title_names.append(name[0].get_text())
        
        # for i in range(len(links)):
        #     print(f"{i}: {title_names[i]}\n{links[i]}")
        # break
        

# %%
