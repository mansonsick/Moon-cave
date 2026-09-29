// Classic worker keeps the same Safari-compatible MediaPipe loading strategy as Story 02.
let detector,vision,canvas,ctx,colour=null,pick=null;
self.onmessage=async({data})=>{
  try{
    if(data.type==='init'){
      const base=new URL('./vendor/mediapipe/',self.location.href);
      const {FilesetResolver,PoseLandmarker}=await import(new URL('vision_bundle.mjs',base).href);
      vision=await import(new URL('./ball-vision.js',self.location.href).href);
      const wasm=await FilesetResolver.forVisionTasks(new URL('wasm/',base).href);
      detector=await PoseLandmarker.createFromOptions(wasm,{baseOptions:{modelAssetPath:new URL('pose_landmarker_lite.task',base).href,delegate:'CPU'},runningMode:'VIDEO',numPoses:2,minPoseDetectionConfidence:.6,minPosePresenceConfidence:.6,minTrackingConfidence:.6,outputSegmentationMasks:false});
      canvas=new OffscreenCanvas(160,120);ctx=canvas.getContext('2d',{willReadFrequently:true});
      self.postMessage({type:'ready'});
    }else if(data.type==='pick'){pick=data.point;colour=null;}
    else if(data.type==='frame'&&detector){
      try{
        const result=detector.detectForVideo(data.bitmap,data.at);let ball=null;
        if(data.catch){
          const ratio=160/Math.max(data.bitmap.width,data.bitmap.height);
          canvas.width=Math.round(data.bitmap.width*ratio);canvas.height=Math.round(data.bitmap.height*ratio);
          ctx.drawImage(data.bitmap,0,0,canvas.width,canvas.height);
          const pixels=ctx.getImageData(0,0,canvas.width,canvas.height);
          if(pick){colour=vision.pickColour(pixels,pick.x,pick.y);pick=null;}
          ball=vision.findBall(pixels,colour);
        }
        self.postMessage({type:'pose',poses:result.landmarks,ball,colorReady:!!colour,at:data.at});
      }finally{data.bitmap.close();}
    }
  }catch{self.postMessage({type:'error'});}
};
