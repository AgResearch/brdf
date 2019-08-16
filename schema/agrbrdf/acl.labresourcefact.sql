--
-- Name: labresourcefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE labresourcefact FROM PUBLIC;
REVOKE ALL ON TABLE labresourcefact FROM agrbrdf;
GRANT ALL ON TABLE labresourcefact TO agrbrdf;
GRANT SELECT ON TABLE labresourcefact TO gbs;


