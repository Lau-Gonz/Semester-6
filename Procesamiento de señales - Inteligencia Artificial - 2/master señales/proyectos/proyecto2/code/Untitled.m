recObj = audiorecorder(16000, 24, 1);
fs = recObj.SampleRate; % Extrayendo la frecuencia de muestreo del objeto de grabación.
time =2;
recordblocking(recObj, time);
            
% extraer el audio
datosGrabacion = getaudiodata(recObj);
datosGrabacion = datosGrabacion ./ max(datosGrabacion);

%%

% El amor es una locura que ni el cura cura,que si el cura lo cura es una locura del cura.
% Pablito clavó un clavito; ¿qué clavito clavó Pablito?
% El viejo cangrejo se quedó perplejo al ver su viejo reflejo en aquel espejo
% El Otorrinolaringólogo trabaja en la otorrinolaringología.
% 

filename = 'yo_dave.wav';
audiowrite(filename, datosGrabacion, fs);

%%

% probar el audio
sound(datosGrabacion,fs);
%%
% procesar la información
n = length(datosGrabacion);
t = (0:n-1)/fs;

%graficar la señal de audio
plot(t, datosGrabacion);
xlim([0 time]);


%%
[coeffs, delta, deltaDelta, loc] = mfcc(datosGrabacion, fs, 'NumCoeffs', 30);
plot(coeffs)
title('MFCCs')

%%

F = repelem([1 2], [99]);
F = categorical(F)';

%%



%%
[B,dev,stats] = mnrfit(coeffs, F);





