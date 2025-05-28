import request from '@/app/_utils/service';
import { ConfigProvider } from 'antd';
import { Metadata } from 'next';
import { Inter } from 'next/font/google';
import theme from '../theme/themeConfig';
import { PRIMARY_COLOR, PRIMARY_COLOR_LIGHT } from './_constants';
import StyledComponentsRegistry from './_ui/antd-registry';

import { ClientHeadersProvider } from '@/app/providers/clientHeaders';
import { I18nProvider } from '@/app/providers/i18n';
import { getPlatformFromUserAgent } from '@/utils';
import { headers } from 'next/headers';
import Script from 'next/script';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: {
        template: '%s | OpenLoong',
        default: 'OpenLoong',
    },
    description:
        'OpenLoong是全球领先的、综合性的人形机器人开源社区，社区秉持着技术驱动和开放透明的价值观，致力于汇聚全球开发者，共同推动人形机器人产业的发展，为全球人形机器人产业赋能。',
    icons: {
        icon: '/logo.png',
    },
    generator: '人形机器人',
    applicationName: '人形机器人',
    keywords: [
        '人形机器人',
        'OpenLoong',
        '具身智能',
        '机器人社区',
        '机器人论坛',
        '机器人开发者社区',
        '机器人技术论坛',
        '机器人开源',
        '开源机器人',
        '潜龙在源',
        '机器人数据集',
        '具身数据集',
        '具身大模型',
        'humanoid robot',
        'Embodied AI',
        '机器人',
        '智能机器人',
    ],
    creator: '人形机器人',
    publisher: ' OpenLoong',
    metadataBase: new URL('https://www.openloong.org.cn'),
};

const getTheme = () => {
    return request('/openloong-api/theme/findTheme', {
        method: 'GET',
    });
};

let grayMode: boolean = false;
let hoverColor: string = PRIMARY_COLOR_LIGHT;
let themeColor: string = PRIMARY_COLOR;

const RootLayout = async ({ children }: { children: React.ReactNode }) => {
    const res = await getTheme();
    const headersList = await headers();

    if (res.ok && res.data) {
        const { gray_mode, hover_color, theme_color } = res.data;
        grayMode = gray_mode;
        hoverColor = hover_color;
        themeColor = theme_color;
    }
    const userAgent = new Map(headersList).get('user-agent');
    const platform = getPlatformFromUserAgent(userAgent ?? '');
    return (
        <html
            lang="cn"
            style={
                {
                    '--primary-color': themeColor,
                    '--primary-light-color': hoverColor,
                    filter: grayMode && 'grayscale(100%)',
                    // h1: isMobile ? '32px' : '24px',
                } as React.CSSProperties
            }
        >
            <head>
                {platform.isMobile && (
                    <meta
                        name="viewport"
                        content="width=device-width, initial-scale=0.6, maximum-scale=0.6, minimum-scale=0.6"
                    />
                )}
                <Script
                    async
                    src="https://www.googletagmanager.com/gtag/js?id=G-HLE5GV9ENS"
                ></Script>
                <Script>
                    {`
                        window.dataLayer = window.dataLayer || [];
                        function gtag(){dataLayer.push(arguments);}
                        gtag('js', new Date());

                        gtag('config', 'G-HLE5GV9ENS');
                     `}
                </Script>
            </head>
            <body className={`${inter.className}`}>
                <StyledComponentsRegistry>
                    <I18nProvider>
                        <ClientHeadersProvider headers={headersList}>
                            <ConfigProvider
                                theme={{
                                    ...theme,
                                    token: {
                                        ...theme.token,
                                        colorPrimary: themeColor,
                                    },
                                }}
                            >
                                {children}
                            </ConfigProvider>
                        </ClientHeadersProvider>
                    </I18nProvider>
                </StyledComponentsRegistry>
                <script
                    type="text/javascript"
                    dangerouslySetInnerHTML={{
                        __html: `var _hmt = _hmt || [];
                        (function() {
                            var hm = document.createElement("script");
                            hm.src = "https://hm.baidu.com/hm.js?808b40ddd91cb47db7d8c923b50c235c";
                            var s = document.getElementsByTagName("script")[0]; 
                            s.parentNode.insertBefore(hm, s);
                        })();
                    `,
                    }}
                ></script>
            </body>
        </html>
    );
};

export default RootLayout;
