---
layout:     post
title:      "Do You Really Need An i7"
subtitle:   "Convincing people that your robot need more cpu power."
date:       2016-03-30 4:17:00
author:     "Shikher Verma"
header-img: "img/posts/chip-bg.jpg"
comments: true
tags: [ CodeMonkey ]
---

## When Raspberry Pi 2 and Odroid U3 fail you. What next ? Back to x64.

Initially Shikher thought that buying a low power armh processor was a very wise choice. Low power meant lower battery consumption so lighter batteries. Also single chip armh processors like Raspberry Pi and Odroid are way cheaper. The world was good. Until one day OpenCV came along. Initially he seemed like a nice guy. Resourceful. With his awesome HighGUI and shiny high power tools like HoughCircle, Contrast stretching he seemed like a guy Shikher could rely on. But soon Shikher became so dependant on him that he forgot the limited hardware that had to support OpenCV. The world started breaking apart. Shikher was caught up between using powerful tools of OpenCV or making the resource requirements low for odroid u3 and raspberry pi 2 boards. Eventually it became clear that there was no other way, Shikher started looking for stronger boards which could meet the requirements of OpenCV. He soon came across NUC; One of the most powerful boards used in robotics projects. Although the specs were great but it came with a big setback to our budget, and using it also meant increased battery consumption. Shikher tried to weigh to pros and cons of it and presented this to my team so that they will go forward with the purchase.

## Weighing the pros and cons
Pros:

1. Currently our image processing nodes take a lot of cpu usage. This is because a lot of OpenCV functions are lengthy matrix operations. One way is to reduce the frame rate so that once the last frame was processed we take the latest frame and process it; dropping all the frames in between. But this leads to very low fps and uneven rate of output. For better accuracy we need to run the image processing at the fps of camera rather than being limited by our processing speed. Other than this the filter on sensor data are also resource hungry and even though right now we don't have complicated motion control and planning but later that too will require more processing power.
2. Shifting to a 64 bit architecture makes software development easier because both rpi and odroid were armh architecture which had limited support in terms of precompiled binaries. We even encountered a bug which is armh specific.
3. We are developing this auv not just for a competition but also to serve as a platform for doing underwater robotics research. In the future when we research and test more and more sophisticated algorithms we would want the testing platform to be free of any limitations.
4. We are running Raspberry pi 2 (and earlier Odroid u3) in headless mode (without GUI) because we don't have enough processing power to support GUI.
5. With surplus resources we will have the freedom to experiment and add more features like running a webserver with the controls and output data exposed as a web page.
6. In addition to this we also have the roscore, motion library and sensor nodes which have significant resource requirements. We expect the current requirements to increase because we will be running multiple task handlers, increasing the complexity in motion library and adding various debug nodes like a dashboard, system diagnostics and data logger.

Cons:

1. Shifting to a more powerful processor would increase the battery requirement.
2. But it can be managed by using batteries of higher capacity.

## Create Report

Hmm, how to log cpu usage. How to do this?
May be capture output of some monitor periodically against the pid of our process ?
What to use ? ```top```/```htop```/```ps``` ?
```ps```'s output seems easily processable. 

1. Start all the nodes and note their pid (process indentifier).

2. So after starting all the ros nodes and roscore we need to log the output of ps periodically. Writing a script to log ps output. Luckily there was already such a thing writen. I found [```Syrupy```](https://github.com/jeetsukumaran/Syrupy) which does exactly this.

Time (s) | i5 CPU% | rpi CPU%	
:-------:|:-------:|:--------:
1	|	29	|	70.2
2	|	26	|	75.9
3	|	25.6	|	95.4
4	|	25	|	93.7
5	|	25.4	|	94.2
6	|	24.6	|	95.6
7	|	21.2	|	95.4
8	|	21.3	|	95.3
9	|	21.1	|	95.4
10	|	21.2	|	95.4

![graph-i5-rpi](/img/posts/graph-i5-rpi.png "graph to show the difference better")

## NUC who?
Intel *N*ext *U*nit of *C*omputing is a 64 bit motherboard + Processor kit. Along with it you will have to buy Ram and SSD. For anyone looking to upgrade their robot's cpu I suggest buying Intel NUC NUC5i7RYH.  
Buying it : [NUC](http://www.amazon.in/intel-core-i7-NUC5i7RYH-kit/dp/B00WAS1FX6?tag=googinhydr18418-21)  
Mandatory Accessories to Buy: [RAM](http://www.amazon.in/Kingston-RAM-LAPTOP-1600MHZ-PC3L/dp/B00CQ35HBQ/ref=pd_bxgy_147_3?ie=UTF8&refRID=0WM2SPDHFSSG4FR3BZ88) [SSD](http://www.amazon.in/CRUCIAL-250-GB-SATA-CT250MX200SSD6/dp/B00RZ6GO98/ref=pd_bxgy_147_2?ie=UTF8&refRID=0WM2SPDHFSSG4FR3BZ88)  
Information links : [Product Brief](http://www.intel.com/content/www/us/en/nuc/nuc-kit-nuc5i7ryh-brief.html) [Product Overview](http://www.intel.com/content/www/us/en/nuc/nuc-kit-nuc5i7ryh.html)  
Powering it : [forum discussion](http://forums.trossenrobotics.com/showthread.php?6316-Intel-NUC&s=366a85b68bb5d63dcf80397b0c52fe94&p=59110#post59110) [Voltage Regulator](http://www.amazon.com/dp/B008FLE7PA/ref=pe_385040_30332190_pe_175190_21431760_M3T1_ST1_dp_1)  
Integrating RAM and MiniSSD: [video](https://www.youtube.com/watch?v=SU4cdMm-8Qc)

## Planning to use Raspberry and Odroid too.
After all this, I also ordered a router. Now we are planning to run nuc, rpi and odroid all together so the whole ros software can be distributing across the whole linux cluster. This would also provide support for low power mode, when battery is low we can switch off nuc and use minimal control via rpi to bring auv back surface. Also fault tolerance is introduced. Even if one of the boards fail the rest can work in emergency.
