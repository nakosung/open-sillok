// Exercise actual server/search/date/export routes without starting a web server.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import ts from 'typescript';
const root=fileURLToPath(new URL('../',import.meta.url));
const cache=new Map();
async function moduleUrl(filename){
  if(cache.has(filename))return cache.get(filename);
  let source=await fs.readFile(filename,'utf8');
  if(filename.endsWith('.json'))source=`export default ${source};`;
  let code=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
  const imports=[...code.matchAll(/\bfrom\s+["']([^"']+)["']/g)];
  for(const match of imports){
    const specifier=match[1];assert(specifier.startsWith('.')||specifier.startsWith('@/'),`Unexpected runtime import: ${specifier}`);
    let target=specifier.startsWith('@/')?path.join(root,specifier.slice(2)):path.resolve(path.dirname(filename),specifier);
    if(!path.extname(target))target+='.ts';
    code=code.replace(match[0],`from ${JSON.stringify(await moduleUrl(target))}`);
  }
  const url=`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`;cache.set(filename,url);return url;
}
const getModule=async name=>import(await moduleUrl(path.join(root,name)));
const {entries,edition,searchEntries,entryDate,citation,sourceUrl,catalogSearch}=await getModule('lib/annals.ts');
const includes=(query,id)=>assert(searchEntries(query).some(e=>e.id===id),query);
assert.equal(searchEntries('').length,entries.length);
includes('훈민정음','kda_12512030_002');includes('장영실','kda_12403016_002');includes('史官','kca_10402008_004');includes('rain vessel','kda_12308018_004');includes('１４０４ horse','kca_10402008_004');
assert.equal(searchEntries('zzzz-not-in-this-edition').length,0);assert.equal(searchEntries('horse','Jeongjo','Astronomy').length,0);
assert(searchEntries('','Taejong').every(e=>e.king==='Taejong'));
const topic=entries[0].topics[0];assert(searchEntries('','all',topic).length>0);assert(searchEntries('','all',topic).every(e=>e.topics.includes(topic)));
const hangul=entries.find(e=>e.id==='kda_12512030_002');assert(!entryDate(hangul).includes('day'));assert(entryDate({...hangul,dateScope:undefined,leapMonth:true}).includes('intercalary'));
assert(citation(hangul).includes(sourceUrl(hangul)));assert(citation(hangul).includes('not independently reviewed'));
for(const entry of entries){assert(citation(entry).includes(entry.id));assert(citation(entry).includes(entry.translationSha256.slice(0,12)));}
const first=catalogSearch('','all','all',0,17),second=catalogSearch('','all','all',17,17);assert.equal(first.nextOffset,17);assert.equal(new Set([...first.items,...second.items].map(e=>e.id)).size,34);assert(!('original' in first.items[0]));assert(!('translation' in first.items[0]));
const search=await getModule('app/api/entries/route.ts');
for(const query of ['offset=-1','offset=1.5','limit=51','limit=0','limit=oops',`q=${'a'.repeat(301)}`])assert.equal(search.GET(new Request(`https://example.test/api/entries?${query}`)).status,400,query);
assert.equal((await search.GET(new Request('https://example.test/api/entries?offset=99999')).json()).items.length,0);
assert.equal((await search.GET(new Request('https://example.test/api/entries?q=훈민정음')).json()).items[0].id,hangul.id);
const single=await getModule('app/api/entries/[id]/route.ts');assert.equal((await single.GET(new Request('https://example.test'),{params:Promise.resolve({id:'missing'})})).status,404);
assert.equal((await (await single.GET(new Request('https://example.test'),{params:Promise.resolve({id:hangul.id})})).json()).original,hangul.original);
const downloadRoute=await getModule('app/api/edition/route.ts');const response=downloadRoute.GET();assert.equal(response.status,200);assert(response.headers.get('content-disposition').includes(`sillok-edition-${edition.version}.json`));
const download=await response.json();assert.equal(download.entries.length,entries.length);for(const e of download.entries){assert.equal(e.sourceUrl,sourceUrl(e));assert(e.provenance.contributors.length>0);assert.equal(e.originalSha256,e.provenance.sourceSha256);}
const packRoute=await getModule('app/api/work-packs/[id]/route.ts');
for(const id of ['missing','__proto__','../../project'])assert.equal((await packRoute.GET(new Request('https://example.test'),{params:Promise.resolve({id})})).status,404);
const packResponse=await packRoute.GET(new Request('https://example.test'),{params:Promise.resolve({id:'kca_10401007_002'})});const pack=await packResponse.json();assert.equal(packResponse.status,200);assert.equal(pack.kind,'translate');assert.equal(pack.source.original,'○三府獻壽于經筵廳。');assert.equal(pack.source.originalSha256,pack.translation.provenance.sourceSha256);assert(pack.instructions.includes('every clause'));assert.equal(pack.targetPath,'content/en/kca/kca_10401007_002.json');
for(const file of ['components/reading-room.tsx','components/entry-reader.tsx','components/work-board.tsx']){const content=await fs.readFile(path.join(root,file),'utf8');assert(!content.includes('@/lib/annals')&&!content.includes('@/data/entries'),'Full corpus must stay out of client imports');}
console.log(JSON.stringify({search:'passed',pagination:'passed',datePrecision:'passed',citations:'passed',download:'passed',workPacks:'passed',apiErrors:'passed',entries:entries.length}));
