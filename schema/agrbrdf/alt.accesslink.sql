--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accesslink
    ADD CONSTRAINT "$1" FOREIGN KEY (ob) REFERENCES ob(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accesslink
    ADD CONSTRAINT "$2" FOREIGN KEY (staffob) REFERENCES staffob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY accesslink
    ADD CONSTRAINT "$3" FOREIGN KEY (oblist) REFERENCES oblist(obid);


