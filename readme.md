### A Dictionary/ Language Translation Plugin For Wox

### Dictionary

This feature is totally based on [Bing](https://cn.bing.com/dict) web site.

Dictionary for chinese and english:

![](./img/word.gif)

refer to web site:

![](./img/word.png)



### Translation

Translate from your sentence to any other languages:

![](./img/sentence.gif)

#### Enable It

Please fill the `appid` and `secretKey`  before you using the translation feature. You can get them on [Baidu translation open platform](http://api.fanyi.baidu.com/)，and apply the [General Translation API](http://api.fanyi.baidu.com/product/11) service.

Then open the plugin directory and edit the `conifg.json` and fill in the values:

``` python
{
    "app_id": "your appid ni baidu fanyi API platform",
    "secret_key": "your secretKey ni baidu fanyi API platform",
}
```

Then you are good to go.

#### More Language?

By default, the plugin will translate the original sentence to `en/zh`.

You can decide what kind of languages you want as the target language by edting the `conifg.json`:

``` python
"target_languages" : [
    "zh", 
    "en",
    "jp", 
    "kor"
]
```

You can add or remove languages in this setting with the language in [list](http://api.fanyi.baidu.com/doc/21).

