// usage: node shot.mjs <jobs.json>   jobs: [{file, out, wait?, w?, h?}]
// Loads each local .geolibre.json in the live GeoLibre Web app (web.geolibre.app/?url=...), serving the file through
// Playwright request interception (no local server / no loopback CORS), then screenshots the page.
import fs from 'fs'; import { createRequire } from 'module';
const { chromium } = createRequire((process.env.PLAYWRIGHT_DIR||'/workspace/geolibre-render')+'/')('playwright-core');
const jobs=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
for(const j of jobs){
  const p=await b.newPage({viewport:{width:j.w||1400,height:j.h||900},deviceScaleFactor:1});
  const errs=[]; p.on('console',m=>{if(m.type()==='error')errs.push(m.text().slice(0,200))});
  await p.route('https://render.invalid/**',r=>r.fulfill({status:200,contentType:'application/json',headers:{'Access-Control-Allow-Origin':'*'},body:fs.readFileSync(j.file)}));
  await p.goto('https://web.geolibre.app/?url='+encodeURIComponent('https://render.invalid/p.geolibre.json'),{waitUntil:'domcontentloaded',timeout:90000});
  await p.waitForTimeout(j.wait||15000);
  await p.addStyleTag({content:'.bookmark-panel,.maplibregl-ctrl-top-right,.maplibregl-ctrl-top-left{display:none!important}'});
  await p.waitForTimeout(500);
  const m=p.locator('.maplibregl-map').first();
  if(await m.count()) await m.screenshot({path:j.out}); else await p.screenshot({path:j.out});
  console.log(JSON.stringify({out:j.out,errors:errs.slice(0,5)}));
  await p.close();
}
await b.close();
