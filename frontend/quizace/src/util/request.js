// 引入axios
import axios from 'axios';


let baseUrl="http://localhost:8000/api"
//创建axios实例
const httpService = axios.create({
    //url前缀-"http:xxx.xxx*
    //baseURL：process.env.BASE_API，//需自定义
    baseURL:baseUrl,
    //请求超时时间
    timeout:3000,//需自定义
});

//添加请求和响应拦截器
//添加请求拦截器
httpService.interceptors.request.use(function (config){
    //在发送请求之前做些什么
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, function (error) {
    //对请求错误做些什么
    return Promise.reject(error);
});

//添加响应拦截器
httpService.interceptors.response.use(function (response){
    //对响应数据做点什么
    return response;
}, function (error) {
    //对响应错误做点什么
    return Promise.reject(error);
});


/* get请求
url:请求地址
params:参数 */

export function get(url, params = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'get',
            params: params
        }).then(response => {
            resolve(response);
        }).catch(error => {
            reject(error);
        });
    });
}

/* post请求
url:请求地址
params:参数
config:配置项 */

export function post(url, params = {}, config = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'post',
            // 对于POST请求，使用data属性传递参数
            // 对于FormData类型，直接使用data属性
            // 对于普通对象，使用data属性
            ...(params ? { data: params } : {}),
            ...config
        }).then(response => {
            console.log(response);
            resolve(response);
        }).catch(error => {
            console.log(error);
            reject(error);
        });
    });
}

/* put请求
url:请求地址
params:参数
config:配置项 */

export function put(url, params = {}, config = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'put',
            ...(params ? { data: params } : {}),
            ...config
        }).then(response => {
            resolve(response);
        }).catch(error => {
            reject(error);
        });
    });
}

/* delete请求
url:请求地址
params:参数 */

export function del(url, params = {}, config = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'delete',
            params: params,
            ...config
        }).then(response => {
            console.log(response);
            resolve(response);
        }).catch(error => {
            console.log(error);
            reject(error);
        });
    });
}

/* 文件上传
url:请求地址
params:参数 */

export function fileUpload(url, params = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'post',
            data: params, // 使用data属性传递文件数据
            // 移除手动设置的Content-Type，让axios自动处理
        }).then(response => {
            resolve(response);
        }).catch(error => {
            reject(error);
        });
    });
}

export function getServerUrl(){
    return baseUrl
}

export function getMediaBaseUrl(){
    return getServerUrl().replace(/\/api\/?$/, '')
}

export default{
    get,
    post,
    put,
    del,
    fileUpload,
    getServerUrl,
    getMediaBaseUrl
}