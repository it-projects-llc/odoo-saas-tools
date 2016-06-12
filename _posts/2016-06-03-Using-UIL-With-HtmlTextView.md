---
layout: post
title: "Using UIL Library with Image Getter to load HTML Images in a TextView"
subtitle: ""
date: 2016-06-03 01:20:00
author: "Shikher Verma"
header-img: "img/posts/android-bg.jpg"
comments: true
tags: [ CodeMonkey ]
---
*This blog post assumes that the reader has a clear understanding of Basic Android Development.*

Presenting HTML data in an Android application is problematic. For instance, if you have a big junk of HTML, you may use a Web View; however it would become awfully slow for multiple independent pieces. As an alternative you can use a TextView. Unfortunately TextView doesn't support all the HTML tags, even some common ones. Luckily, there is a nice library called `HtmlTextView` which adds support for most of the common tags. Although loading images in TextView is a pain, the load time is large and it is always loaded in the memory. Thus if your images are large, you will soon get an OutOfMemory Error (OOM). For android this limit is around 20MB of Ram. Popular image loading and caching libraries mostly set an image directly to the ImageView. However, there is a workaround for using Universal Image Loader Library (UIL) for loading and caching images. It turns out you can give your custom implementation of ImageGetter (an interface) to load images.

Following is an implementation of ImageGetter which fetches images using UIL:
{% gist ShikherVerma/740ccdc1e4021aec78078df2857449b9 HuracanImageGetter.java %}

Now setting HTML to HtmlTextView (which is a descendant of TextView) with the new ImageGetter:
{% gist ShikherVerma/740ccdc1e4021aec78078df2857449b9 SetHtmlToTextView.java %}

After this, you can also resize the image to fit into a screen size. Doing it after caching would be wrong because then each time
image would be resized after loading from the cache. So resizing should be done before caching, and not in the ImageGetter implementation. This class would be later used in the `Application.java` file as shown later.
{% gist ShikherVerma/740ccdc1e4021aec78078df2857449b9 HuracanBitmapProcessor.java %}

Setting the default preferences for universal image in the application. These are some of the default things that need to be done in order to tell the UIL to set preferences like using cache.
{% gist ShikherVerma/740ccdc1e4021aec78078df2857449b9 HuracanApplication.java %}
