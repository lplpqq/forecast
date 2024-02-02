import { Text } from '@radix-ui/themes';
import { PropsWithChildren } from 'react';

export interface HeaderProps {

};

const Header = ({ }: PropsWithChildren<HeaderProps>) => {
    return (
        <div className='flex flex-row px-8 py-2 justify-between'>
            <Text>Weather Forecast</Text>
            <div></div>
        </div>
    );
};

export default Header;
