from  requests import  get
from  filetype import guess
from  os import  rename
from  os  import  makedirs
from  os.path  import exists
from  json import  loads
from  contextlib import  closing
import  random
import  os
import  queue
import  threading


# user_agent列表
user_agent_list = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'
]
#文件下载器
def Down_load(file_url,file_full_name,now_photo_count,all_photo_count):
    mutex_lock = threading.Lock()
    headers = {'User-Agent': random.choice(user_agent_list)}
    mutex_lock.acquire()
    with closing(get(file_url,headers=headers,stream=True)) as response:
        chunk_size = 1024 #单次最大请求值
        content_size = int(response.headers['content-length']) #文件总大小
        data_count = 0 #当前已经传输的大小
        with open(file_full_name,"wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                done_block = int((data_count / content_size) *50)
                data_count = data_count + len(data)
                now_jd = (data_count /content_size) * 100
                print("\r %s：[%s%s] %d%% %d/%d" % (file_full_name, done_block * '█', ' ' * (50 - 1 - done_block), now_jd, now_photo_count, all_photo_count), end=" ")
        #下载完图片后获取图片扩展名,并为其增加扩展名
        file_type = guess(file_full_name)
        rename(file_full_name,file_full_name + '.' + file_type.extension);

        # #释放锁
    mutex_lock.release()

def get_desk_p():
   return os.path.join(os.path.expanduser('~'), "Desktop")
#爬取不同类型图片
def crawler_photo(type_id,photo_count):
    #最新 1,最热 2,女生 3,星空 4
    if (type_id == 1):
        url = 'https://service.paper.meiyuan.in/api/v2/columns/flow/5c68ffb9463b7fbfe72b0db0?page=1&per_page=' + str(
            photo_count)
    elif (type_id == 2):
        url = 'https://service.paper.meiyuan.in/api/v2/columns/flow/5c69251c9b1c011c41bb97be?page=1&per_page=' + str(
            photo_count)
    elif (type_id == 3):
        url = 'https://service.paper.meiyuan.in/api/v2/columns/flow/5c81087e6aee28c541eefc26?page=1&per_page=' + str(
            photo_count)
    elif (type_id == 4):
        url = 'https://service.paper.meiyuan.in/api/v2/columns/flow/5c81f64c96fad8fe211f5367?page=1&per_page=' + str(
            photo_count)
    #获取图片列表数据
    headers = {'User-Agent': random.choice(user_agent_list)}
    respond =get(url,headers)
    photo_data = loads(respond.content)
    #已经下载的图片张数
    now_photo_count = 1

    #所有图片张数
    all_photo_count =len(photo_data)
    
    # #开始下载并保存5k分辨率壁纸
    #将所有基金代码放入先进先出FIFO队列中
    # 队列的写入和读取都是阻塞的,姑在多线程情况下不会乱
    # 在不使用框架的前提下,引入多线程,提高爬取效率
    # 创建一个队列
    fund_code_queue = queue.Queue(all_photo_count)
    # 写入基金代码数据到队列
    #for i in range(all_photo_count):
        # fund_code_list[i]也是list类型，其中该list中的第0个元素存放基金代码
        #fund_code_queue.put(photo_data[i])



    for photo in photo_data:
        #创建一个文件夹存放我们下载的图片
        desktop = get_desk_p() +"/PYDownImages"
        if not exists(desktop + str(type_id)):
            makedirs(desktop + str(type_id))
        #准备下载的图片链接
        file_url = photo['urls']['raw']

        #准备下载的图片名称,不包含扩展名
        file_name_only = file_url.split('/')
        file_name_only = file_name_only[len(file_name_only)-1]
        #准备保存到本地的完整路径
        file_full_name = desktop +str(type_id) + "/" + file_name_only
        #开始下载图片
        # Down_load(file_url,file_full_name,now_photo_count,all_photo_count)
        fund_code_queue.put((file_url,file_full_name,now_photo_count,all_photo_count));
        #now_photo_count = now_photo_count + 1
#当队列不为空
    while ( not fund_code_queue.empty()):
        #从队列读取一个基金代码
        #读取是阻塞操作
        fund_code = fund_code_queue.get()
        print(fund_code);
        #使用try,except来捕获异常
        #如果不捕获异常,程序可能崩溃
        try:
            # # 使用代理访问
            # # 创建一个线程锁,防止多线程写入文件时候发生错乱
            #
            # # 线程数为50,在一定范围内,线程数越多,速度越快
            # for i in range(50):
            #     t = threading.Thread(target=Down_load,args=(fund_code[0],fund_code[1],now_photo_count,fund_code[3]), name="LoopThread" + str(i))
            #     t.start()

             Down_load(fund_code[0],fund_code[1],now_photo_count,fund_code[3])
             now_photo_count = now_photo_count + 1

            # #申请获取锁,此过程为阻塞等待状态,直到获取锁完毕
            # mutex_lock.acquire()
            # #追加数据写入csv文件,若文件不存在则自动创建
            # str11 = get_desk_p() + '/fund_data.csv'
            # print(str11)
            # with open(str11,'a+',encoding="utf-8") as csv_file:
            #     csv_writer = csv.writer(csv_file)
            #     data_list = [x for x in data_dict.values()]
            #     csv_writer.writerow(data_list)
            # #释放锁
            # mutex_lock.release()
        except Exception:
            #访问失败了,所以要把我们刚才取出的数据再放回队列中
            fund_code_queue.put(fund_code)
            print("访问失败,尝试再次下载")



if __name__ == '__main__':
        #最新1, 最热2, 女生 3, 星空 4
        #爬取类型为3的图片,一个20000张
        wall_paper_id = 1;
        wall_paper_count = 10;
        while(True):
            #换行符
            print('\n\n')
            print("你好")
        # 选择壁纸类型
            wall_paper_id = input("壁纸类型：最新壁纸 1, 最热壁纸 2, 女生壁纸 3, 星空壁纸 4\n请输入编号以便选择5K超清壁纸类型：")
        # 判断输入是否正确
            while (wall_paper_id != str(1) and wall_paper_id != str(2) and wall_paper_id != str(3) and wall_paper_id != str(4)):
                wall_paper_id = input("壁纸类型：最新壁纸 1, 最热壁纸 2, 女生壁纸 3, 星空壁纸 4\n请输入编号以便选择5K超清壁纸类型：")
        # 选择要下载的壁纸数量
            wall_paper_count = input("请输入要下载的5K超清壁纸的数量：")
        # 判断输入是否正确
            while (int(wall_paper_count) <= 0):
                wall_paper_count = input("请输入要下载的5K超清壁纸的数量：")

        # 开始爬取5K高清壁纸
            print("正在下载5K超清壁纸，请稍等……")

#
            crawler_photo(int(wall_paper_id), int(wall_paper_count))
            print('\n下载5K高清壁纸成功!')