import {getWorkPack} from "@/lib/work-packs";
export async function GET(_request:Request,{params}:{params:Promise<{id:string}>}){
  const {id}=await params;const pack=getWorkPack(id);
  if(!pack)return Response.json({error:"Prepared source not found"},{status:404});
  return Response.json(pack,{headers:{"Content-Disposition":`attachment; filename="open-sillok-${id}.json"`,"Cache-Control":"public, max-age=300","X-Content-Type-Options":"nosniff"}});
}
