--
-- Name: biosubjectfk; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY t_animal_fact
    ADD CONSTRAINT biosubjectfk FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


