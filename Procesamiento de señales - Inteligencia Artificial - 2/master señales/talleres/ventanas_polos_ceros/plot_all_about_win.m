function [] = plot_all_about_win(freq, time, freq_response, title_)


    %plot de la magnitud en frecuencia
    %plot de 2 filas 4 columnas donde para este plot
    %en particular se toma la primera y la segunda celda
    figure, subplot(2,4, [1 2]);
    sgtitle(title_);
    semilogy(freq, abs(freq_response));
    title('Respuesta en frec.')
    xlabel('Freq [Hz]');
    ylabel('Amplitud [u.a.]'); %unidades arbitrarias
    grid on;

    %plot del angulo de la frecuencia
    %para este plot en particular se toma la 3ra y la 4ta celda
    subplot(2,4, [3 4]) ;
    plot(freq, angle(freq_response));
    title('Ángulo');
    xlabel('Freq [Hz]');
    ylabel('Angulo [u.a.]'); %unidades arbitrarias
    grid on;
    
    %Generar respuesta en frecuencia completa del filtro
                                         %flip left to right
    L_H_C = [freq_response(1:end-1) conj( fliplr(freq_response(2:end)) ) ]; 

    %Obtener la respuesta al impulso 
    l_h = real(ifft(L_H_C));    %por errores numéricos la ifft no es puramente real 
                                %por lo tanto se le saca la parte real

    %para este plot en particular se toma la 6ta y la 7tima celda
    subplot(2, 4, [6 7])
    plot(time(1:end/2), l_h(1:end/2)); %por la simetría la señal se puede cortar a la mitad
    title('Respuesta al impulso');
    grid on
    xlabel('time [s]')
    ylabel('Amplitud [u.a.]')         %unidades arbitrarias


end