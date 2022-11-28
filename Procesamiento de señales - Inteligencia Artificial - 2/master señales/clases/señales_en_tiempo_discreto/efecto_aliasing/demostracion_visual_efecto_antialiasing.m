%frecuencia de simulación

F_si = 1000;        %mil muestras en un segundo para simular tiempo continuo
t = 0:1/F_si:10;    %tiempo 'continuo'
f = 1;              %frecuencia
x = sin(2*pi*f*t);  %creación de la señal
F_s = f*5;          %frecuencia de muestreo

%es recomendable para lograr reconstruir mejor las cosas usar 5 veces 
%la frecuencia max, como freq de muestreo

figure, plot(t, x);
hold on 

%voy a muestrear la señal x     %fix hace lo mismo que floor
t_m = t(1:fix(F_si/F_s):end)    %genero los tiempos de muestreo    
x_m = x(1:fix(F_si/F_s):end)    
stem(t_m, x_m)
plot(t_m, x_m, 'r--')
