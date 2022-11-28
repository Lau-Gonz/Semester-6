%% toma los nombres de los archivos de testeo

main_path = "data\test\";
files = ["p1.wav" "p2.wav" "p3.wav" "p4.wav" "p5.wav" ...
         "p6.wav" "p7.wav" "p8.wav" "dave1.wav" "dave2.wav" ...
         "dave3.wav" "dave4.wav" "dave5.wav" "dave6.wav" "dave7.wav" ...
         "dave8.wav" "dayana1.wav" "dayana2.wav" "dayana3.wav" ... 
         "dayana4.wav" "dayana5.wav" "dayana6.wav" "dayana7.wav" ...
         "dayana8.wav"];
     
ytest = [3 3 3 3 3 3 3 3 1 1 1 1 1 1 1 1 2 2 2 2 2 2 2 2];


%% carga la matriz de betas y hace las predicciones 

%load("betas.mat");

predictions = [];


for i = 1:length(files)
    path = strcat(main_path, files(i));
    [signal, fs]  = audioread( path ); 
    [prob, classification] = regresion_logistica_test( signal, fs);
    predictions = [predictions; classification];
end
%% Matriz de confusion
C = confusionmat(ytest,predictions,'Order',[1 2 3]);
confusionchart(C)

%% graficar otra cosa

[audioIn,fs] = audioread("data\test\dayana2.wav");
Regresion_test_matrizxonfusion(betas, audioIn, fs)

%% Graficas que se utilizan en el informe
xtest = mfcc(audioIn, fs, 'NumCoeffs', 13); 
n = length(audioIn);
f = (-n/2:n/2-1)*fs/n;
f = (0:n/2-1)*fs/n; 
m = 1127.0148*log(1+(f/700));
plot(f,m)
grid on
title('\emph{\textbf{Frecuencia vs Frecuancia Mel}}', 'Interpreter', 'latex')
xlabel('\textbf{Frecuencia}  \textit{[Hz]}', 'Interpreter','latex')
ylabel('\textbf{Frecuencia Mel} \textit{[mels]} ', 'Interpreter','latex')







