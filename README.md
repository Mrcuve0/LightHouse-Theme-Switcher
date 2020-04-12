# Lighthouse Theme Switcher

## Automatically switch your Plasma Theme (& more) according to the time of the day.

[![DevelopmentStatus](https://img.shields.io/badge/Development-Ongoing-brightgreen.svg)](https://img.shields.io/badge/Development-Ongoing-brightgreen.svg)
[![HitCount](http://hits.dwyl.com/Mrcuve0/Lighthouse-Theme-Switcher.svg)](http://hits.dwyl.com/Mrcuve0/Lighthouse-Theme-Switcher) 

![Twitter Follow](https://img.shields.io/twitter/follow/Mrcuve0?label=Follow%20Me%21%20%40Mrcuve0&style=social)

![LightHouse Demo](screenshots/LightHouse-Demo.gif)


Table of contents
=================
<!--ts-->
- [Lighthouse Theme Switcher](#lighthouse-theme-switcher)
  - [Automatically switch your Plasma Theme (& more) according to the time of the day.](#automatically-switch-your-plasma-theme--more-according-to-the-time-of-the-day)
- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
  - [1.1. **What *Lighthouse* can do?**](#11-what-lighthouse-can-do)
  - [1.2. **What *Lighthouse* cannot do (for now)**](#12-what-lighthouse-cannot-do-for-now)
  - [1.3. **What's for the future of *Lighthouse*?**](#13-whats-for-the-future-of-lighthouse)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Repo Development Info](#repo-development-info)
- [Donations](#donations)
- [License](#license)
<!--te-->

Introduction
===

## 1.1. **What *Lighthouse* can do?**

**Lighthouse Theme Switcher** is a simple "all-in-one" `python3` script able to change the overall theme in a KDE Plasma environment: you invoke it and everything is switched in a matter of seconds.

As for now, it can handle the following components:

* KDE Plasma's **Global Theme**
* KDE Plasma's **GTK3 Theme**
* KDE Plasma's **Wallpaper**
* KDE Plasma's **Konsole default profile**

## 1.2. **What *Lighthouse* cannot do (for now)**

As for now, **Lighthouse Theme Switcher** cannot handle a switching activity based on daytime.

To do that, you can however bind **Lighthouse** to a CronJob in order to invoke it at specific times of the day.

Please, refer to the **wiki** to discover how to do that.

## 1.3. **What's for the future of *Lighthouse*?**

- [x] Switch **Plasma Global Theme**
- [X] Switch **Wallpaper**
- [X] Switch **GTK3 Theme**
- [X] Switch **Konsole Theme**
- [ ] Drop the use of **Cron** to handle the switch according to the time of the day (too cumbersome to setup)
- [ ] Switch theme according to Sunrise and Sunset at current location (**geoclue2**?)
- [ ] Lighthouse deamon (**systemd service**?)
- [ ] Better Plasma integration (**Plasmoid**?)

Let me know what you think, feel free to [DM me on Twitter](https://twitter.com/mrcuve0) or open an issue specifying your future request.

Dependencies
===
No particular dependency is required, you just need `python3` to launch it. 
Most (if not all) distros come with `python3` pre-installed.

Installation
===
Please, refer to the related section in the **wiki**.

Usage
===
Please, refer to the related section in the **wiki**.

Repo Development Info
===
Please, refer to the badges "`development`" you can find at the top of each README, here's some additional infos:

1. [![DevelopmentStatus](https://img.shields.io/badge/Development-Ongoing-brightgreen.svg)](https://img.shields.io/badge/Development-Ongoing-brightgreen.svg)
> This means I'm currently enhancing/fixing the project. I'm open to suggestions and Pull Requests, that will be treated as soon as possible.
2. [![DevelopmentStatus](https://img.shields.io/badge/Development-Paused-yellow.svg)](https://img.shields.io/badge/Development-Paused-yellow.svg)
> This means I'm currently not considering the project as a top priority, hence issues and Pull Request will be still treated, but with higher delays. The development status can reach a higher priority ("Ongoing") or a lower one "Stopped" at any time.
3. [![DevelopmentStatus](https://img.shields.io/badge/Development-Stopped-red.svg)](https://img.shields.io/badge/Development-Stopped-red.svg)
> This means I'd prefer to consider this project abandoned. I could reconsider this development status only if some really big opportunities present itselves and really worth the effort. Issues and PR will be probably read but not considered.

*As a general rule*, take in mind that my entire [GitHub profile](https://github.com/Mrcuve0) (themes included!) is based on my sparse time and it is mainly passion-driven. As for now, *my number one priority* is finishing my **Master's Degree in Embedded Systems**: don't panic if I cannot reply to your issue even after a week, I'm probably really busy and I'm making already restless nights.

Donations
===

> I hope that this theme is to your liking and I hope that, as it was in my case, this can become your everyday theme.
>
> I am sure you will appreciate all the work behind this repo and the many hours of my free time that I have dedicated (and will continue to devote) to this project.
> 
> If you want, you can consider a small donation to support future developments for this and many new projects that will come in the future.
>
> Thank you for your time.
> 
>Mrcuve0

Below you'll find infos on how you can do it:

1. Donate via PayPal [![alt text](https://www.paypal.com/en_US/i/btn/btn_donate_LG.gif)](https://paypal.me/mrcuve0)

2. Donate via LiberaPay [![alt text](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/Mrcuve0/donate)

3. I also accept feeless and miner-free cryptocurrencies, here's my **IOTA address**:
```
OSYUR9NE9SV9LYGFWOAWAPXSQCXEITZXRKHSVSXIKYXUUSGIMIJZMSKCXZBVZRYUVMVS9KYNENVZVVULADJWOUUYBX
```
![alt text](https://raw.githubusercontent.com/Mrcuve0/Aritim-Dark/master/QRCode.jpg)

License
===

**Lighthouse Theme Switcher** is licensed under the [GLPv3 license](https://github.com/Mrcuve0/Lighthouse-Theme-Switcher/blob/master/LICENSE).

I always try to be as correct and thankful as possible: if you see some inconsistencies on licenses please be free to open an issue/PR for this repo and explain the problem. I will reply ASAP and fix the issue. The last thing I want to do is to harm someone else's IP. 

Of course, I'm expecting the same treatment in case you'll decide to publish modifications of my projects.

Finally, like *Daft Punk* said:

> We Are Human After All


