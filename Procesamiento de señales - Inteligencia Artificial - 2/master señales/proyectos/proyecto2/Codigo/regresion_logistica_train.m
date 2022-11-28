function [B] = regresion_logistica_train()
    
    %archivos con los datos de entrenamiento
    files = ["data\train\123_dave.wav", "data\train\sapo_dave.wav", "data\train\colores_dave.wav", ...
         "data\train\123_dayana.wav", "data\train\sapo_dayana.wav", "data\train\colores_dayana.wav", ...
         "data\train\sapo_esteban.wav", "data\train\sapo_edward.wav", ...
         "data\train\sapo_nelson.wav", "data\train\sapo_mariana.wav", ...
         "data\train\sapo_laura.wav", "data\train\sapo_ana.wav", "data\train\trabalenguas_cura_dayana.wav", ...
         "data\train\trabalenguas_cura_dave.wav", "data\train\trabalenguas_pablito_dayana.wav", ...
         "data\train\trabalenguas_pablito_dave.wav", "data\train\trabalenguas_cangrejo_dave.wav", ...
         "data\train\trabalenguas_cangrejo_dayana.wav", ...
         "data\train\s1.wav", "data\train\s2.wav", "data\train\s3.wav", ...
         "data\train\s4.wav", "data\train\s5.wav", "data\train\s6.wav", ...
         "data\train\s7.wav", "data\train\s8.wav", "data\train\sdave.wav",...
         "data\train\sdayana.wav", "data\train\traje_dave.wav", "data\train\baño_dave.wav", ...
         "data\train\paco_dave.wav", "data\train\pepe_dave.wav", "data\train\poquito_dave.wav", ...
         "data\train\propone_dispone_dave.wav", "data\train\toto_dave.wav", ...
         "data\train\traje_dayana.wav", "data\train\baño_dayana.wav", ...
         "data\train\paco_dayana.wav", "data\train\pepe_dayana.wav", "data\train\poquito_dayana.wav", ...
         "data\train\propone_dispone_dayana.wav", "data\train\toto_dayana.wav", ...
         "data\train\noise.wav", "data\train\noise2.wav", ...
         "data\train\noise3.wav", "data\train\noise4.wav"]; 
     
     %etiquetas de las categorias de cada uno de los archivos
     %respectivamente
     %1 -> dave
     %2 -> dayana
     %3 -> otro
     
    file_label  = [1 1 1 2 2 2 3 3 3 3 3 3 2 1 2 1 1 2 3 3 3 3 3 3 3 3 1 2 1 1 1 1 1 1 1 ...
        2 2 2 2 2 2 2 3 3 3 3];

        
    %% calculo de todos los coeficientes
    
    ks = [];      %Guarda los numeros de ventanas de cada mfcc para cada señal
    xtrain = [];  %Guarda todos los coeficientes de las mfcc para cada señal
                  %(cada coeff del mfcc es guardado uno debajo del otro)


    for file = 1:length(files)

        [signal, fs]  = audioread( files(file) );   %lee la muestra de audio
        signal = signal./max(signal);           %normaliza la muestra de audio

        %filtro pasa bandas desde los 20Hz hasta 4kHz (para quitar el ruido)
        [b, a] = butter(4, [20/(fs/2), 4000/(fs/2)]);
        filtered_signal = filter(b, a, signal);

        %calcula los coefs de la mfcc
        [coeffs, delta, deltaDelta, loc] = mfcc(filtered_signal, fs, 'NumCoeffs', 38);

        %obtienen la cantidad de ventanas de los coeffs size(coeffs)(1)
        coefsDim = size(coeffs);
        ks = [ks; coefsDim(1)];

        %guarda todos los coefs uno bajo el otro en una matriz
        xtrain = [xtrain; coeffs];
        
    end
    
    %% creación de las etiquetas

    ytrain = [];     %contiene las etiquetas correspondientes a cada una de las 
                     %ventanas de la mfcc de la señal

    for labelnum = 1:length(ks)

        a = file_label(labelnum);
        b = ks(labelnum);
        labels = repelem([a], [b])';    
        ytrain = [ytrain; labels];
    end
    
    
    B = mnrfit(xtrain, ytrain);
end

