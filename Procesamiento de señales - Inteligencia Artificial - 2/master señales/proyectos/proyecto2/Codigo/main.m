load 'betas.mat'

%% testeo con audio en vivo
    
recObj = audiorecorder(16000, 24, 1);

% Extrayendo la frecuencia de muestreo del objeto de grabación.
fs = recObj.SampleRate;             
time =3;
recordblocking(recObj, time);
            
% extraer el audio
datosGrabacion = getaudiodata(recObj);

%%
sound(datosGrabacion, fs);

%% revision del resultado
[prob1, person1] = regresion_logistica_test(betas, datosGrabacion, fs)


%% testeo con audio grabado

path =  "data/test/muchacho.wav";
[signal2, fs2]  = audioread( path ); 


%% revision del resultado
[prob2, person2] = regresion_logistica_test(betas, signal2, fs2)
