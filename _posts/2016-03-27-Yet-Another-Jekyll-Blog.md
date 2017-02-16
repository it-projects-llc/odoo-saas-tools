---
layout:     post
title:      "Yet Another Jekyll Blog"
subtitle:   "The Birth of yet another jekyll blog, which would be soon lost in oblivion."
date:       2016-03-27 17:00:00
author:     "Shikher Verma"
header-img: "img/posts/jekyll-bg.jpg"
comments: true
tags: [ CodeMonkey ]
---

**Note : Click <a href="#customize">this</a> to skip to the part where I explain about customizing this theme for your use.**

## How this blog was created
![Clean Blog](/img/posts/heartvbrain1.png)

## What? Why? Jekyll?

Jekyll is a static website generator thats designed for building minimal, static blogs. Whats special about Jekyll is that Github Pages supports it. Meaning that you won't have to setup a local workstation and build the site locally. You can directly push the jekyll project and github will automatically build and serve the generated static website. Even though I prefer to use local build for testing out changes before pushing, still it makes things easier as I don't have to maintain separate branches for source and generated website.
Jekyll (and other static site generators) have a considerable advantage over other blogging platforms like wordpress. Its minimal. No database, no backend. You design your blog instead of struggling with complicated backend issues. And the best part is you outsource hosting to github.

## Setting up and customizing a Jekyll Blog

### A.Pick a template

If you are (lazy like me) and don't want to write CSS, HTML & Javascript for frontend; you can checkout these resources to choose a jekyll template:

* [Jekyll Official List](https://github.com/jekyll/jekyll/wiki/themes)
* [themes.jekyllrc.org](http://themes.jekyllrc.org/)
* [jekyllthemes.io](http://jekyllthemes.io/)
* [jekyllthemes.org](http://jekyllthemes.org/)

Or you can take the middle path and choose a HTML template. Make a jekyll theme out of it like me. Some of the best places to find them are :

* [Html5Up](https://html5up.net/)
* [StartBootstrap](https://startbootstrap.com/template-overviews/clean-blog/)

I chose [Clean Blog](http://startbootstrap.com/template-overviews/clean-blog/) because I wanted a plain old fashion website. Most of the jekyll templates I found were too funky for my taste. Bright colors, unconventional navigation patterns.


![Clean Blog](https://startbootstrap.com/img/templates/clean-blog.jpg)

### B.Hosting

This part is awesome. You don't have to worry about pricing or uptime. Just outsource it to github!
What you have to do is create a github repository named ```username.github.io``` and push your jekyll project to the master branch. Github will automatically build and serve the generated website at ```http://username.github.io``` Aye! Captain Obvious here. You have to replace username with your github username.

<a name="customize"></a>

### C. Customize it

Most probably no matter which theme you choose you will want to tweak something in it. I added a lot of things; below I'll try to explain how I did it and how you can tweak parts of my website for your use or remove them if not needed.

**Index**

1. <a href="#prerequisites">Prerequisites</a>
2. <a href="#3-steps">Build your website in 3 steps</a>
3. <a href="#newpage">Add a new page</a>
4. <a href="#newpost">Add a new blog post</a>
5. <a href="#newtag">Add new blog tags and tag specific pages</a>
6. <a href="#blogpage">Clickable tags shown in blog page</a>
7. <a href="#subfolder">Landing page different than blog</a>
8. <a href="#comments">Comments using Disqus</a>
9. <a href="#analytics">Website stats using Google Analytics</a>
10. <a href="#email">Email subscription using FeedBurner</a>
11. <a href="#collection">Jekyll collection for portfolio</a>
12. <a href="#travisCI">Travis build script to verify builds and external links</a>
13. <a href="#domain">Add custom domain name</a>
14. <a href="#misc">Miscellaneous awesome stuff</a>

<a name="prerequisites"></a>**1. Prerequisites**

* You need to have a GitHub account. If you don't have one, [sign up here](https://github.com/join) - it takes one minute. This is where your website will live - if you sign up with username `someone` then your website will be `http://someone.github.io`.  
* It would be helpful to understand what Markdown is and how to write it. Markdown is just a way to take a piece of text and format it to look a little nicer.  For example, this whole instruction set that you're reading is written in markdown - it's just text with some words being bold/larger/italicized/etc. I recommend taking 5 minutes to learn markdown [with this amazingly easy yet useful tutorial](http://markdowntutorial.com/).

<a name="3-steps"></a>**2. Build your website in 3 steps**

Getting started is *literally* as easy as 1-2-3 :)  
Scroll down to see the steps involved, but here is a 40-second video just as a reference as you work through the steps.

![Installation steps](/img/posts/install-steps.gif)

1. Fork the theme on github : Fork this website by going to the [github page of this project](https://github.com/shikherverma/shikherverma.github.io/) and click the *Fork* button on the top right corner. Forking means that you now copied this whole project and all the files into your account.
2. Change the project name in settings : This will create a GitHub User page ready with the *CleanBlogEnhanced* template that will be available at `http://<yourusername>.github.io` within a couple minutes.  To do this, click on *Settings* at the top (the cog icon) and there you'll have an option to rename.

3. Change data : Edit the `_config.yml` file to change all the settings to reflect your site. To edit the file, click on it and then click on the pencil icon (watch the video tutorial above if you're confused).  The settings in the file are fairly self-explanatory and I added comments inside the file to help you further. Any line that begins with a pound sign (`#`) is a comment, and the rest of the lines are actual settings.

Another way to edit the config file (or any other file) is to use [prose.io](http://prose.io/), which is just a simple interface to allow you to more intuitively edit files or add new files to your project.  
After you save your changes to the config file (by clicking on *Commit changes* as the video tutorial shows), your website should be ready in a minute or two at `http://<yourusername>.github.io`. Every time you make a change to any file, your website will get rebuilt and should be updated in about a minute or so.  
You can now visit your shiny new website, which will be seeded with several sample blog posts and a couple other pages. Your website is at `http://<yourusername>.github.io` (replace `<yourusername>` with your user name). Do not add `www` to the URL - it will not work!  
**Note:** The video above goes through the setup for a user with username `daattalitest`. I only edited one setting in the `_config.yml` file in the video, but *you should actually go through the rest of the settings as well. Don't be lazy, go through all the settings :)*

<a name="newpage"></a>**3. Add a new page**

To add pages to your site, you can either write a markdown file (`.md`) or you can write an HTML file directly.  It is much easier to write markdown than HTML, so I suggest you do that (use the [tutorial I mentioned above](http://markdowntutorial.com/) if you need to learn markdown). You can look at some files on this site to get an idea of how to write markdown. To look at existing files, click on any file that ends in `.md`, for example [`this blog post`](https://github.com/ShikherVerma/Shikherverma.github.io/blob/master/_posts/2016-03-27-Yet-Another-Jekyll-Blog.md). On the next page you can see some nicely formatted text (there is a word in bold, a link, bullet points), and if you click on the pencil icon to edit the file, you will see the markdown that generated the pretty text. Very easy!  
In contrast, look at [`index.html`](https://github.com/ShikherVerma/Shikherverma.github.io/blob/master/index.html). That's how your write HTML - not as pretty. So stick with markdown if you don't know HTML.

If you want to show this page in the top navigation bar of the website you have to edit [_includes/nav.html](https://github.com/ShikherVerma/Shikherverma.github.io/blob/master/_includes/nav.html). Just add an entry similar to the one present for blog or resume pointing to your new page or folder.

```
<li>
    <a href="/blog/">blog</a>
</li>
```
If you don't want the URL to end with `.html` you can create a folder with the desired name and place an `index.html` in it. Similar to what I have done for [blog](https://github.com/ShikherVerma/Shikherverma.github.io/blob/master/blog/).

<a name="newpost"></a>**4. Add a new blog post**

Any file that you add inside the [`_posts`](https://github.com/ShikherVerma/Shikherverma.github.io/blob/master/_posts) directory will be treated as a blog entry.  To publish a blog post add a file in `_post/` folder. Lets say `2016-03-27-Untitled-Post.md`. Notice that the file name contains today’s date and the title of your post. Jekyll requires posts to be named year-month-day-title.md. You can look at the existing files there to get an idea of how to write blog posts.  After you successfully add your own post, you can delete the existing files inside [`_posts`](https://github.com/ShikherVerma/Shikherverma.github.io/blob/master/_posts) to remove the sample posts, as those are just demo posts to help you learn.

 As mentioned previously, you can use [prose.io](http://prose.io/) to add or edit files instead of doing it directly on GitHub, it can be a little easier that way.

*Important thing: YAML front matter ("parameters" for a page)*

In order to have your new pages use this template and not just be plain pages, you need to add [YAML front matter](http://jekyllrb.com/docs/frontmatter/) to the top of each page. This is where you'll give each page some parameters that I made available, such as a title and subtitle. I'll go into more detail about what parameters are available later. If you don't want to use any parameters on your new page (this also means having no title), then use the empty YAML front matter:

```
---
---
```

If you want to use any parameters, write them between the two lines. For example, you can have this at the top of a page:

```
---
title: Contact me
subtitle: Here you'll find all the ways to get in touch with me
---
```

*Important takeaway: ALWAYS add the YAML front matter, which is two lines with three dashes, to EVERY page. If you have any parameters, they go between the two lines.*    
If you don't include YAML then your file will not use the template.

*YAML front matter parameters*

These are the main parameters you can place inside a page's YAML front matter that *CleanBlogEnhanced* supports.

Parameter   | Description
----------- | -----------
title       | Page or blog post title
subtitle    | Short description of page or blog post that goes under the title
comments    | If you want do add Disqus comments to a specific page/post, use `comments: true`.
date       | Date of publishing for a blog post.
author   | Author of the blog post.
tags       | List of tags for the blog post.
header-img       | Personalized image for blog post that will show up in the header, use `header-img: /path/to/img`.
layout      | What type of page this is (default is `blog` for blog posts and `page` for other pages. You can use `default` if you don't want a header image)  


*Page layout types*

* post - To write a blog post, add a markdown or HTML file in the `_posts` folder. As long as you give it YAML front matter (the two lines of three dashes), it will automatically be rendered like a blog post. Look at the existing blog post files to see examples of how to use YAML parameters in blog posts.
* page - Any page outside the `_posts` folder that uses YAML front matter will have a very similar style to blog posts.
* default - If you want to create a page with minimal styling (ie. without the bulky header image), assign `layout: default` to the YAML front matter.
* If you want to completely bypass the template engine and just write your own HTML page, simply omit the YAML front matter. Only do this if you know how to write HTML!

<a name="newtag"></a>**5. Add new blog tags and tag specific pages**

To add new tags you have to create a new file in `blog/tags`. This so that each tag can have a customized url and a page with posts filtered with that tag.

<a name="blogpage"></a>**6. Clickable tags shown in blog page**

On the blog page, instead of description, tags are listed. To add any tag to the list of tags below title, you have add it to `tags` yaml front matter in `blog/index.html`.

<a name="subfolder"></a>**7. Landing page different than blog.**

Currently blog is not the default landing page. You can make blog the default page by doing the following :

* Removing the `index.html` outside of any folders.
* Move out the contents `blog` folder and remove the empty `blog` folder.
* In `_config.yml` replace all `/blog/` with `/`

<a name="comments"></a>**8. Comments using Disqus**

If you want to enable comments on your site, CleanBlogEnhanced supports the [Disqus](https://disqus.com/) comments plugin.  To use it, simply sign up to Disqus and add your Disqus shortname to the `disqus` parameter in the `_config.yml`. To turn on comments on any page or blog post, add `comments: true` to the YAML front matter. Or if you want to remove this feature, you can simply make the value in `_config.yml` empty.

<a name="analytics"></a>**9. Website stats using Google Analytics**

Google Analytics can be added to track page views. CleanBlogEnhanced lets you easily add Google Analytics to all your pages. This will let you track all sorts of information about visits to your website, such as how many times each page is viewed and where (geographically) your users come from.  To add Google Analytics, simply sign up to [Google Analytics](http://www.google.com/analytics/) to obtain your Google Tracking ID, and add this tracking ID to the `google_analytics` parameter in `_config.yml`. Or if you want to remove this feature, you can simply make the value in `_config.yml` empty.

<a name="email"></a>**10. Email subscription using FeedBurner**

You can allow users to subscribe to new blog posts using [FeedBurner](https://feedburner.google.com). To add FeedBurner just sign up on the service and replace the url in `_config.yml`. Or if you want to remove this feature, you can simply make the value in `_config.yml` empty.

<a name="collection"></a>**11. Jekyll collection for portfolio**

My landing page includes my portfolio, ie. showcase of some of my best projects. I have used a jekyll collection to avoid copy pasting huge amount of code. The `index.html` takes up data from `_portfolio` folder. So if you want to customize the portfolio items you can change the data there. Also for this data to be available in `index.html` I had to add it as a collection in `_config.yml`. If this part is not required by you, you can delete the `collection - portfolio` part from `_config.yml` along with the portfolio folder and relevant section of `index.html`.

<a name="travisCI"></a>**12. Travis build script which verifies all links are working**

Travis CI is a service which lets you build your project each time you update it. Using travis you can check when external link stop not working or whether you last change builds or not. External links are being checked using `html-proofer` which can check a lot of other things too. To use this you have to sign up on [TravisCI](https://travis-ci.org/) and enable build for you website.

<a name="domain"></a>**13. Add custom domain name**

To serve your website on a custom domain like I do, you will have to buy a domain name. Basically you need to set your domain name to point to github. This will be done with you DNS provider. I bought my domain from Namecheap. It was the cheapest DNS provider and costed me ₹600 ($12) for 2015-16 and ₹715 for 16-17. Once that is done, add a new file in the root of your project named CNAME containing your domain name. See github's post on how to add custom domains to github pages [here](https://help.github.com/articles/using-a-custom-domain-with-github-pages/).
If you too use namecheap, you can follow [this guide](http://davidensinger.com/2013/03/setting-the-dns-for-github-pages-on-namecheap/) to setup the DNS.

<a name="misc"></a>**14. Miscellaneous awesome stuff**

* *Read Time Estimation for blog posts*; Each blog post automatically has an estimate of how long it will take to read the blog post.
* *404 page*; Create a `404.html` page in the root directory. Jekyll would automatically serve this if the url is not found.
* *added favicon*; Favicon is the little icon on browser tab. To add it just include a favicon.ico in the root directory.
* *Mobile First*; CleanBlogEnhanced is designed to look great on both large-screen and small-screen (mobile) devices. Load up your site on your phone or your gigantic iMac, and the site will work well on both, though it will look slightly different.
* *Easily Customizable*; Many personalization settings in `_config.yml`, such as setting your name and site's description, customizing the links in the menus, customizing what social media links to show in the footer, etc.
* *RSS feed*; CleanBlogEnhanced automatically generates a simple RSS feed of your blog posts, to allow others to subscribe to your posts.  If you want to remove the link to your RSS feed in the footer change rss to false in the `_config.yml`.
* *Server less search using javascript*; You want your readers to be about to search through the blog, in case the have a broken link this becomes priceless. I used [Simple Jekyll Search](https://github.com/christian-fei/Simple-Jekyll-Search).

## Have Questions / Issues about my website theme or jekyll in general ?
Feel free to ask them in the comments below!
