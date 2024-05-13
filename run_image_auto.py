import os
import cv2
from tqdm import tqdm
from typing import Union
from info_instances import CarInfo, RegistrationProofInfo, SectionInfo


def show_image_with_scale(
        org_img,
        winname: str,
        scale_factor: Union[float, int] = 1
):
    if scale_factor != 1:
        # Define the scaling factor (e.g., resize to half of the original size)
        scale_factor = 0.5  # Change this value to adjust the resize scale

        # Calculate the new dimensions based on the scaling factor
        new_width = int(org_img.shape[1] * scale_factor)
        new_height = int(org_img.shape[0] * scale_factor)

        # Resize the image using cv2.resize()
        image = cv2.resize(org_img, (new_width, new_height))
    else:
        image = org_img

    cv2.imshow(mat=image, winname=winname)
    # Wait for a key press and then close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def make_test_proof_back_page(
        image_template_path,
        car_info: CarInfo,
        debug: bool,
):
    img = cv2.imread(image_template_path)
    img_size = img.shape[:2]
    registration_proof_info = RegistrationProofInfo(
        section_D=SectionInfo(
            value=car_info.get_section_d(),
            position=(img_size[1] // 4, img_size[0] // 6)
        ),
        section_E=SectionInfo(
            value=car_info.vin_number,
            position=(img_size[1] // 4, int(img_size[0] // 2.6))
        ),
        section_H=SectionInfo(
            value=car_info.start_date,
            position=(img_size[1] // 6, 940)
        ),
        section_I=SectionInfo(
            value=car_info.end_date,
            position=(img_size[1] // 6, 1040)
        ),
    )
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    font_thickness = 2
    font_color = (0, 0, 0)

    for section_name, section_info in registration_proof_info.__dict__.items():
        if section_name == 'section_D':
            line_height = 40  # Height between lines
            # Split the text into lines
            lines = section_info.value.split('\n')
            # Write each line of text onto the image
            y_offset = section_info.position[1]  # Starting y-offset
            for line in lines:
                cv2.putText(
                    img, line, (section_info.position[0], y_offset),
                    font, font_scale, font_color, font_thickness, cv2.LINE_AA
                )
                y_offset += line_height  # Move to the next line
        else:
            cv2.putText(
                img, section_info.value, section_info.position,
                font, font_scale, font_color, font_thickness, cv2.LINE_AA
            )

    if debug:
        show_image_with_scale(org_img=img, winname=os.path.basename(image_template_path))
    else:
        save_dir = 'results'
        os.makedirs(save_dir, exist_ok=True)
        output_image_path = os.path.join(
            save_dir,
            f'backpage_{car_info.maker}_{car_info.model}_{car_info.vin_number}_{car_info.plate_number}.png'
        )
        cv2.imwrite(output_image_path, img)


if __name__ == '__main__':
    IMG_PATH = "assets/Template_test_registration_proof.png"
    DEBUG = False

    maker_name = 'Deepal'
    model_name = 'S07'
    start_time = '2024-05-13'
    end_time = '2024-07-12'
    LIST_VIN_PLATE_NUM = [
        ('LS6C3E0M6RF830201', 'W3700P96'),
        ('LS6C3E0M8RF830202', 'W3700P97'),
        ('LS6C3E0MXRF830203', 'W3700P98'),
    ]

    car_instances = [
        CarInfo(maker=maker_name, model=model_name, vin_number=vin_plate_num[0], plate_number=vin_plate_num[1],
                start_date=start_time, end_date=end_time)
        for vin_plate_num in LIST_VIN_PLATE_NUM
    ]
    for car in tqdm(car_instances):
        make_test_proof_back_page(image_template_path=IMG_PATH, car_info=car, debug=DEBUG)
