# Hello-JAVA-Selenium

#### 介绍
学习一下web自动化  
> 其实自动化的工具有很多，但我现在只是JAVA会一点，所以选择学习这个。   
> 自动化工具我看比较多的有python可以做。     

本文基本参考：https://www.cnblogs.com/TankXiao/p/5252754.html    


#### 环境搭建  
> 1. jdk
> 2. IntelliJ IDEA  
```
//新建Maven项目，在pom.xml文件下添加如下依赖
<dependency>
        <groupId>org.seleniumhq.selenium</groupId>
        <artifactId>selenium-java</artifactId>
        <version>4.1.1</version>
</dependency>  
```   
> 3. 每个浏览器都有相应的驱动器   
`https://www.selenium.dev/downloads/` 去这里下载对应浏览器的driver 浏览器也要注意自己的**版本**;  
``` // 配置浏览器驱动，如果正常打开网页，即算配置成功
        System.setProperty("webdriver.chrome.driver", "/Users/zeffect/Documents/lib/chromedriver");
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.xuexi.cn/");
```   

##### 接下来就是元素操作了   
```
driver.findElement(By.id(“id的值”))；
driver.findElement(By.name(“name的值”))；
driver.findElement(By.linkText(“链接的全部文字”))；
driver.findElement(By.partialLinkText(“链接的部分文字”))；
driver.findElement(By.cssSelector(“css表达式”))；
driver.findElement(By.xpath(“xpath表达式”))；
driver.findElement(By.className(“class属性”))；
driver.findElement(By.tagName(“标签名称”))；
  //等待某个页面出现，20秒是超时
  WebDriverWait wait = new WebDriverWait(driver,20);
  wait.until(ExpectedConditions.presenceOfElementLocated(By.id("root")));
  //多窗口操作
  driver.getWindowHandle();
  driver.getWindowHandles();
  driver.switchTo().window("window");
```

