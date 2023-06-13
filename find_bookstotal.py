from ast import keyword
import pandas as pd
import requests,json,datetime,os,re
from time import sleep
from config import CLIENT_ME

MAX_PAGE = 5
HITS_PER_PAGE = 30
REQ_URL = 'https://app.rakuten.co.jp/'\
'services/api/BooksTotal/Search/20170404'
WANT_ITEMS = [
    'booksGenreId',
    #'title','author',
    #'itemUrl',
    #'itemPrice','smallImageUrl',
    'itemCaption'   
]

sta_time = datetime.datetime.today()
this_date = format(sta_time,'%Y%m%d')
path_output_dir = f'./output/{this_date}'
req_params = {
    'applicationId':CLIENT_ME['APPLICATION_ID'],
    'booksGenreId':'001',
    'format':'json',
    'formatVersion':'2',
    'keyword':'',
    #'hits':HITS_PER_PAGE,
    #'sort':'+ireviewCount',
}
#'postageFlag':1 #送料フラグ 0->全て,1->送料込み

def main():

    #本日日付フォルダ作成
    if not os.path.isdir(path_output_dir):
        os.mkdir(path_output_dir)

    #キーワード記載テキストファイルからキーワード配列作成
    with open('list_keyword.txt','r',encoding='utf-8') as f:
        keywords = list(map(str,f.read().split('\n')))

    create_output_data(keywords)

    print(f"{'#'*10}")

def create_output_data(arg_keywords):
    
    #キーワードループ
    for keyword in arg_keywords:
        
        #初期設定
        cnt = 1
        keyword = keyword.replace('\u3000',' ')
        req_params['keyword'] = keyword
        path_file = f'{path_output_dir}/{keyword}.csv'
        df = pd.DataFrame(columns=WANT_ITEMS)

        print(f"{'#'*10}\nNowKeyword --> {keyword}")

        #ページループ
        while True:

            req_params['page'] = cnt
            res = requests.get(REQ_URL,req_params)
            res_code = res.status_code
            res = json.loads(res.text)

            if res_code != 200:
                print(f"ErrorCode --> {res_code}\nError --> {res['error']}\nPage --> {cnt}")
            else:

                #返ってきた商品数の数が0の場合はループ終了
                if res['hits'] == 0:
                    break
                
                tmp_df = pd.DataFrame(res['Items'])[WANT_ITEMS]
                df = pd.concat([df,tmp_df],ignore_index=True)
            
            if cnt == MAX_PAGE:
                break
            
            cnt += 1
            
            #リクエスト制限回避
            sleep(1)
    
        df.to_csv(path_file,index=False,encoding="utf_8_sig",sep=",")
        print(f"Finished!!")

if __name__ == '__main__':
    main()