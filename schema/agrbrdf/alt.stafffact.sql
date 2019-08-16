--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY stafffact
    ADD CONSTRAINT "$1" FOREIGN KEY (staffob) REFERENCES staffob(obid);


