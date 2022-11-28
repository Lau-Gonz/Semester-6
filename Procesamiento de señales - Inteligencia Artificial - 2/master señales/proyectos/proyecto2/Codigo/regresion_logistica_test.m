function [max_val, max_indx] = regresion_logistica_test( signal, fs)
 load("betas.mat", "betas");
%normalizamos la señal
signal = signal./max(signal);

%filtramos el audio para aceptar solo freqs entre 20Hz y 4kHz
cutoff_freqs = [20/(fs/2), 4000/(fs/2)];
[b, a] = butter(4, cutoff_freqs);
filtered_signal = filter(b, a, signal);

%calcula los coefs de la mfcc
xtest = mfcc(filtered_signal, fs, 'NumCoeffs', 38);

%generación de la predicción
results = mnrval(betas, xtest);

%probabilidades de cada clase
probabilities = [mean(results(:,1)) mean(results(:,2)) mean(results(:,3))]; 

[max_val, max_indx] = max(probabilities);

end

