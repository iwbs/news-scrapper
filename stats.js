const path = require('path');
const fs = require('fs');

dirList = ['allianz', 'fidelity', 'ftchinese', 'jpmorgan', 'nytimes', 'pimco', 'ubs', 'zeal'];


const loopFolder = (folderPath) => {
    const result = {
        numOfFile: 0,
        numOfSentence: 0,
        numOfEngWord: 0,
        numOf01ES: 0,
        numOf13ES: 0,
        numOf30ES: 0,
        numOfChiWord: 0,
        numOf01CS: 0,
        numOf13CS: 0,
        numOf30CS: 0,
    };
    const files = fs.readdirSync(folderPath);
    files.forEach(f => {
        const fullPath = path.join(folderPath, f);
        const fpStat = fs.lstatSync(fullPath);
        if (fpStat.isDirectory()) {
            const _ = loopFolder(fullPath);
            result.numOfFile += _.numOfFile;
            result.numOfSentence += _.numOfSentence;
            result.numOfEngWord += _.numOfEngWord;
            result.numOf01ES += _.numOf01ES;
            result.numOf13ES += _.numOf13ES;
            result.numOf30ES += _.numOf30ES;
            result.numOfChiWord += _.numOfChiWord;
            result.numOf01CS += _.numOf01CS;
            result.numOf13CS += _.numOf13CS;
            result.numOf30CS += _.numOf30CS;
        } else if (f !== 'summary.json') {
            const rawdata = fs.readFileSync(fullPath);
            const jsonData = JSON.parse(rawdata);
            let numOfSentence = jsonData.en.length;
            let numOfEngWord = 0;
            let numOf01ES = 0;
            let numOf13ES = 0;
            let numOf30ES = 0;
            let numOfChiWord = 0;
            let numOf01CS = 0;
            let numOf13CS = 0;
            let numOf30CS = 0;
            jsonData.en.forEach(str => {
                const matches = str.match(/[A-z'’-]+/g);
                const count = matches ? matches.length : 0;
                numOfEngWord += count;
                if (count < 10)
                    numOf01ES += 1;
                else if (count >= 10 && count < 30)
                    numOf13ES += 1;
                else
                    numOf30ES += 1;
            });
            jsonData.cn.forEach(str => {
                const matches = str.split("").filter(char => /\p{Script=Han}/u.test(char)).join("");
                const count = matches ? matches.length : 0;
                numOfChiWord += count;
                if (count < 10)
                    numOf01CS += 1;
                else if (count >= 10 && count < 30)
                    numOf13CS += 1;
                else
                    numOf30CS += 1;
            });
            result.numOfSentence += numOfSentence;
            result.numOfEngWord += numOfEngWord;
            result.numOf01ES += numOf01ES;
            result.numOf13ES += numOf13ES;
            result.numOf30ES += numOf30ES;
            result.numOfChiWord += numOfChiWord;
            result.numOf01CS += numOf01CS;
            result.numOf13CS += numOf13CS;
            result.numOf30CS += numOf30CS;
            result.numOfFile++;
        }
    });

    return result;
}

const summary = [];
dirList.forEach(d => {
    const siteStat = loopFolder(d);
    let success_rate = 1;
    try {
        const rawdata = fs.readFileSync(`${d}_summary.json`);
        const jsonData = JSON.parse(rawdata);
        success_rate =  Math.round(jsonData.success / jsonData.total * 1e2) / 1e2;
    } catch (e) {
    }
    summary.push({
        site: d,
        num_of_file: siteStat.numOfFile,
        num_of_sentence: siteStat.numOfSentence,
        num_of_english_word: siteStat.numOfEngWord,
        num_of_less_than_10_e: siteStat.numOf01ES,
        num_of_10_to_30_e: siteStat.numOf13ES,
        num_of_30_plus_e: siteStat.numOf30ES,
        chinese_word_count: siteStat.numOfChiWord,
        num_of_less_than_10_c: siteStat.numOf01CS,
        num_of_10_to_30_c: siteStat.numOf13CS,
        num_of_30_plus_c: siteStat.numOf30CS,
        avg_sentence_per_file: Math.round(siteStat.numOfSentence / siteStat.numOfFile * 1e2) / 1e2,
        avg_eng_word_per_sentence: Math.round(siteStat.numOfEngWord / siteStat.numOfSentence * 1e2) / 1e2,
        avg_chi_word_per_sentence: Math.round(siteStat.numOfChiWord / siteStat.numOfSentence * 1e2) / 1e2,
        success_rate,
    });
})
let data = JSON.stringify(summary, null, 4);
fs.writeFileSync('summary.json', data);
