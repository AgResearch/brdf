--
-- Name: geneticob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticob FROM PUBLIC;
REVOKE ALL ON TABLE geneticob FROM agrbrdf;
GRANT ALL ON TABLE geneticob TO agrbrdf;
GRANT SELECT ON TABLE geneticob TO gbs;


