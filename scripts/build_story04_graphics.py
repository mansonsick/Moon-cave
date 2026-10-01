"""Original simple SVG teaching pictures and UI props, with no embedded words."""
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'stories/story-04/assets/practice'
OUT.mkdir(parents=True,exist_ok=True)
tree='<path fill="#dcebcf" d="M42 66Q17 38 54 29Q66 1 100 25Q132 7 153 37Q188 43 159 72Z"/><path fill="#cfaa7e" d="M93 65h17v70H93z"/><path d="M75 141l26-8 30 8"/>'
bird='<ellipse fill="#c8e0ef" cx="100" cy="78" rx="37" ry="30"/><circle fill="#c8e0ef" cx="130" cy="56" r="23"/><path fill="#f2c569" d="M151 54l22 11-22 10"/><circle fill="#222" cx="135" cy="51" r="3"/><path d="M103 103v18m17-19v19M69 69l-32-17 19 33"/><path d="M90 83q8-23 34-7"/>'
tray='<path fill="#e4c69e" d="M59 122h86l-9 22H68z"/>'
flower='<path d="M103 91v53m0-19q-34-1-26-17 23 1 26 17m0-9q30-21 36-5-20 19-36 5"/><g fill="#f7d7df"><circle cx="103" cy="46" r="19"/><circle cx="81" cy="62" r="19"/><circle cx="89" cy="87" r="19"/><circle cx="116" cy="87" r="19"/><circle cx="126" cy="62" r="19"/></g><circle fill="#ffeab3" cx="103" cy="67" r="17"/>'
envelope='<rect x="64" y="73" width="65" height="37" rx="2" fill="#fff"/><path d="M65 74l31 21 31-21"/>'
table='<path fill="#e4c69e" d="M25 95h155v15H25z"/><path d="M39 110v36m126-36v36"/>'
hand='<path fill="#f5ddc4" d="M153 33l-41 31q-8 4-7 11l3 9q3 10 13 4l42-31"/>'
pictures={
 'mountain':'<path fill="#dcebcf" d="M15 142l41-76 31 50 38-104 63 130Z"/>',
 'water':'<path fill="#dceef5" d="M66 12q65 16 35 46t-6 43q37 12 26 46H52q36-22 14-51t13-36q36-17-13-48"/><path d="M87 25q37 16 5 39m-13 24q-5 16 18 28"/>',
 'sun':'<circle fill="#fff0b2" cx="100" cy="77" r="42"/><path d="M100 8v18m0 103v19M26 77h19m109 0h20M47 24l15 16m78 80 15 16M153 24l-15 16m-76 80-15 16"/>',
 'moon':'<path fill="#fff0b2" d="M126 18q-84 7-75 84 8 66 87 39Q70 95 126 18Z"/>',
 'tree':tree,
 'wood':'<path fill="#e6c59a" d="M38 49l86-14q40 0 46 42t-34 49l-87 6Q14 94 38 49Z"/><ellipse cx="48" cy="91" rx="28" ry="42" fill="#f5e7ce"/><ellipse cx="48" cy="91" rx="17" ry="27"/><ellipse cx="48" cy="91" rx="7" ry="11"/><path d="M82 64l62-10m-59 47 68-11"/>',
 'mouth':'<path fill="#f8d8dd" d="M29 83Q62 44 98 61Q132 41 174 83Q111 139 29 83Z"/><ellipse fill="#fff" cx="100" cy="83" rx="47" ry="18"/>',
 'bird':bird,'flower':flower,
 'bird-above':tree+'<g transform="translate(-4 -7) scale(.45)">'+bird+'</g>',
 'tray-below':tree+tray,
 'taking':table+'<g transform="translate(-10 -41)">'+envelope+'</g>'+hand+'<path stroke="#345c7b" d="M49 89V40l-8 9m8-9 8 9"/>',
 'placing':table+envelope+'<g transform="translate(8 -14)">'+hand+'</g><path stroke="#345c7b" d="M49 40v40l-8-9m8 9 8-9"/>',
 'table-top':table+'<g transform="translate(0 -24)">'+envelope+'</g>',
 'door':'<path fill="#e4c69e" d="M54 146V39q47-59 94 0v107Z"/><circle cx="130" cy="94" r="4"/>'+tray,
 'mountain-shape':'<path stroke="#416954" stroke-width="9" d="M49 47v91h105V47m-51-25v113"/>',
 'water-shape':'<path stroke="#416954" stroke-width="9" d="M104 16q-19 57 0 127m-29-96q-36 33-51 65m104-65 36-17m-35 50 39 35"/>',
 'sun-shape':'<circle stroke="#416954" stroke-width="9" cx="100" cy="80" r="52"/><path stroke="#416954" stroke-width="9" d="M73 80h53"/>',
 'moon-shape':'<path stroke="#416954" stroke-width="9" d="M116 20Q37 39 42 115q9 34 45 32Q66 69 116 20Z"/>',
 'tree-shape':'<path stroke="#416954" stroke-width="9" d="M102 16v129M48 58h107m-52 0-63 68m65-68 57 68"/>',
 'mouth-shape':'<rect stroke="#416954" stroke-width="9" x="46" y="36" width="110" height="92" rx="12"/>',
 'leaf':'<path fill="#b49d59" stroke="#786e4f" d="M30 135Q20 51 163 24q9 97-105 117Z"/><path stroke="#786e4f" d="M27 146l118-101m-82 69-8-26m34 3 22 9"/>',
 'envelope':envelope,'badge':'<path fill="#d2b36a" d="M65 113l-9 37 44-13 44 13-9-37"/><circle fill="#ebd69d" cx="100" cy="72" r="48"/><path d="M75 58h49v31H75zM76 59l24 17 23-17"/>',
 'mailbag':'<path fill="#d1a67a" d="M54 66h94v73H54Z"/><path d="M69 67V47q36-58 66 0v20"/><path fill="#bb8a5a" d="M54 66h94v36H54z"/><path d="M92 92h19v23H92z"/>',
 'leaf-marked':'<path fill="#b49d59" stroke="#786e4f" d="M30 135Q20 51 163 24q9 97-105 117Z"/><path stroke="#786e4f" d="M27 146l118-101"/><g transform="translate(56 47) scale(.45)"><path fill="none" stroke="#66542e" stroke-width="6" d="M30 135Q20 51 163 24q9 97-105 117Z"/><path stroke="#66542e" stroke-width="6" d="M27 146l118-101m-82 69-8-26m34 3 22 9"/></g>',
 'cookies':'<ellipse cx="100" cy="104" rx="80" ry="30" fill="#eee2c9"/><g fill="#c39b66"><circle cx="70" cy="91" r="29"/><circle cx="119" cy="84" r="29"/><circle cx="105" cy="117" r="29"/></g><g fill="#7d553b" stroke="none"><circle cx="61" cy="85" r="4"/><circle cx="79" cy="99" r="4"/><circle cx="114" cy="78" r="4"/><circle cx="129" cy="92" r="4"/><circle cx="97" cy="111" r="4"/><circle cx="113" cy="124" r="4"/></g>',
}
for name,body in pictures.items():
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 160"><g stroke="#303c34" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none">'+body+'</g></svg>'
    (OUT/(name+'.svg')).write_text(svg+'\n',encoding='utf-8')
print('Built',len(pictures),'original SVG teaching pictures/props, no embedded text.')
