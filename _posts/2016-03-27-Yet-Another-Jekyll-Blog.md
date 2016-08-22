---
layout:     post
title:      "Yet Another Jekyll Blog"
subtitle:   "The Birth of yet another jekyll blog, which would probably be soon lost in oblivion."
date:       2016-03-27 17:00:00
author:     "Shikher Verma"
header-img: "img/posts/jekyll-bg.jpg"
comments: true
tags: CodeMonkey
---

## Convincing myself to make this blog

*Brain*: This happens every year. You will be super excited for a couple of weeks and then forget about this completely.  
*Heart*: No!! I want a blog too. All the other hackers have a blog; why can't we have it. This time will be different. I promise to keep posting.  
*Brain*: Really? You don't even have the time to maintain it! You honestly believe that?  
*Heart*: Well...No. But I am going to do it anyway :P  

## What? Why? Jekyll?

Jekyll is a static website generator thats designed for building minimal, static blogs. Whats special about Jekyll is that Github Pages supports it. Meaning that you won't have to setup a local workstation and build the site locally. You can directly push the jekyll project and github will automatically build and serve the generated static website. Even though I prefer to use local build for testing out changes before pushing, still it makes things easier as I don't have to maintain separate branches for source and generated website.

Jekyll (and other static site generators) have a considerable advantage over other blogging platforms. Its minimal. No database, no backend. You design your own blog instead of struggling with complicated pre-build themes. And you outsource hosting to github. 

## Setting up and customizing a Jekyll Blog

### 1.Pick a template

If you are (lazy like me) and don't want to write CSS, Html & Javascript for frontend; you can checkout these resources to choose a template:

* [Jekyll Official List](https://github.com/jekyll/jekyll/wiki/themes)
* [themes.jekyllrc.org](http://themes.jekyllrc.org/)
* [jekyllthemes.io](http://jekyllthemes.io/)
* [jekyllthemes.org](http://jekyllthemes.org/)

I chose [Clean Blog](http://startbootstrap.com/template-overviews/clean-blog/):
![Clean Blog](https://startbootstrap.com/img/templates/clean-blog.jpg)

### 2.Hosting and adding custom domain

This part is awesome. You don't have to worry about pricing or uptime. You outsource it to github!
What you have to do is create a github repository named ```username.github.io``` and push your jekyll project to the master branch. Github will automatically build and serve the generated website at ```http://username.github.io``` Aye! Captain Obvious here. You have to replace username with your github username.

To serve your website on a custom domain like I do, you will have to buy a domain name. Basically you need to set your domain name to point to github. This will be done with you DNS provider. I bought my domain from Namecheap. It was the cheapest DNS provider and costed me ₹600 for 2015-16 and ₹715 for 16-17. Once that is done, add a new file in the root of your project named CNAME containing your domain name. See github's post on how to add custom domains to github pages [here](https://help.github.com/articles/using-a-custom-domain-with-github-pages/).

### 3.Customize it

Most probably no matter which theme you choose you will want to tweak something in it. I added these things to my blog.

* *added 404 page* create a ```404.html``` page in the root directory. Jekyll would automatically serve this 
* *added favicon* favicon is the little icon on browser tab. Add a favicon.ico in the root directory.
* *added search* you want your readers to be about to search through the blog, in case the have a broken link this becomes priceless. I used [Simple Jekyll Search](https://github.com/christian-fei/Simple-Jekyll-Search).
* *added tags* I followed this [guide](http://www.mikeapted.com/jekyll/2015/12/30/category-and-tag-archives-in-jekyll-no-plugins/)
* *displaying tags and read time estimate*
* *added disqus comments*
* *added Google analytics*
* *moved blog to /blog subdirectory*
* *forwarded blog.domain to domain/blog*

### 4.Adding posts

Now coming to our primary concern. To publish a blog post add a file in ```_post/``` folder. Lets say ```2016-03-27-Untitled-Post.md```. Notice that the file name contains today’s date and the title of your post. Jekyll requires posts to be named year-month-day-title.md.
Update the front matter at the beginning of the file.

### Update [2016-05-28]
As of May 2016; 6 people have forked my jekyll theme.
So technically this is my most popular open source project :)
