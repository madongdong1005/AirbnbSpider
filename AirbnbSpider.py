import random
import csv,json
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.common import exceptions
import time
from lxml import etree


class AirbnbSpider(object):

    def __init__(self):

        option = ChromeOptions()
        option.add_argument('--headless')
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_argument("--disable-blink-features=AutomationControlled")
        self.bro = webdriver.Chrome(executable_path="./tools/chromedriver.exe", options=option)
        self.bro.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                                 {"source": """Object.defineProperty(navigator, 'webdriver', 
                                 {get: () => undefined})"""})
        self.bro.maximize_window()

        self.start_url = "https://www.airbnb.cn/"
        self.f = open(f"./data/{self.__class__.__name__}.json", 'w', encoding='utf-8')
        # self.csv_f = csv.writer(self.f)

    def search(self):
        self.bro.get(self.start_url)
        input_box = self.bro.find_element_by_xpath("//input[@id='Koan-via-HeroController__input']")
        input_box.clear()
        input_box.send_keys("浙江省绍兴市")
        but = self.bro.find_element_by_xpath("//button[@class='_1je6u3q']")
        but.click()
        time.sleep(2)
        return self.bro.page_source

    def parse_html(self):
        for page_source in self.get_all_page():
            a_nodes = etree.HTML(page_source).xpath("//div[@class='_qlq27g']/a")
            for a_node in a_nodes:
                item={}
                item["detail_url"] = "https://www.airbnb.cn" + a_node.xpath(".//@href")[0]
                item["house_style"] = "".join(map(lambda x: x.strip(), a_node.xpath(".//div[@class='_wuffzwa']//text()")))
                item["simple_describe"] = a_node.xpath(".//div[@class='_goi623']//text()")[0]
                item["price"] = "".join(map(lambda x:x.strip(), a_node.xpath(".//div[@aria-label='listing_card_price_label']//text()")))
                item["evaluation"] = a_node.xpath("//span[@class='_1clmxfj']/text()")[0]
                self.bro.get(item["detail_url"])
                # item["html"] = self.bro.page_source
                time.sleep(random.randint(5, 10))
                commons = []
                while True:
                    try:
                        but = self.bro.find_element_by_xpath("//li[@class='_ljpfeqr']/button")
                        a = self.bro.find_element_by_xpath("//li[@class='_ljpfeqr']/button/div[@class='_17012i']")
                    except exceptions.NoSuchElementException as e:
                        a = None
                        print(e)
                        break
                    if a:
                        common_divs = self.bro.find_elements_by_xpath("//section/div[2]/div[5]/div")[1:]
                        for common_div in common_divs:
                            reviewer = common_div.find_element_by_xpath(".//div[@class='_w97dxc0']").text
                            public_time = common_div.find_element_by_xpath(".//span[@class='_1xgl77cd']").text
                            content = common_div.find_element_by_xpath("./div/div[2]//div[@dir='ltr']").text
                            commons.append([reviewer, public_time, content])
                        but.click()
                        time.sleep(2)

                item["commons"] = commons
                print(item)
                self.f.write(json.dumps(item, ensure_ascii=False)+",\n")
                self.f.flush()
                # self.csv_f.writerow([item["detail_url"],
                #                      item["house_style"],
                #                      item["simple_describe"],
                #                      item["price"],
                #                      item["evaluation"],
                #                      # item["html"],
                #                      ])
                self.bro.back()
                time.sleep(random.randint(5, 10))

    def get_all_page(self):
        yield self.search()
        while True:
            try:
                next_page = self.bro.find_element_by_xpath("//div[@class='_99vlue']/nav//a[@aria-label='下一个']")
                next_page.click()
                time.sleep(2)
                yield self.bro.page_source
            except exceptions.NoSuchElementException as e:
                print("最后一页", e)
                break




a = AirbnbSpider()
a.parse_html()
# {'detail_url': 'https://www.airbnb.cn/rooms/44623509?previous_page_section_name=1000',
#  'house_style': '整间Loft·1室1卫2床',
#  'simple_describe': '【丁丁民宿】loft/简约清新/鲁迅故里/世贸/银泰/火车站/颐高广场',
#  'price': '价格￥205',
#  'evaluation': '4.6分 · 12条评论',
#  'commons': [['Jing', '2021年3月', '系统自动评论:该房东在房客入住当天单方面取消了订单｡'],
#              ['Fff', '2021年3月', '挺好的挺好的'],
#              ['佳琦', '2021年1月', '挺好的'],
#              ['魔仙堡清洁工', '2020年12月', '房间很适合聚会'],
#              ['辉', '2020年12月', '系统自动评论:该房东在房客入住 9 天前单方面取消了订单｡'],
#              ['Grit', '2020年11月', '提议都在评论里了,希望能改进,给后续客户更好的体验｡'],
#              ['铭含', '2020年11月', '很新的公寓楼,有电梯 房间设施也挺好,洗漱空间宽敞｡是Loft,休息在楼上,楼下是客厅 刚开始觉的有点儿偏,后来发现去火车站,鲁迅故里,仓桥直街车程都是10分钟左右,10几元钱就到了,很方便 而且位置很显眼,好找,停车就在楼下,方便不贵(2小时免费,24小时封顶20元)']
#              ]}
